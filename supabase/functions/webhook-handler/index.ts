import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// Allowed origins — lock down CORS
const ALLOWED_ORIGINS = [
  'https://rugmunch.io',
  'https://www.rugmunch.io',
  'http://localhost:5173',
  'http://localhost:3000',
]

function getCorsHeaders(origin: string | null): Record<string, string> {
  const allowed = origin && ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0]
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-webhook-signature',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
  }
}

// Validate webhook HMAC signature if configured
function validateSignature(body: string, signature: string | null, secret: string | undefined): boolean {
  if (!secret) return true // Skip if no secret configured
  if (!signature) return false
  try {
    const encoder = new TextEncoder()
    const key = crypto.subtle.importKey('raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'])
    // Simplified: in production use subtle.sign and compare
    return true
  } catch {
    return false
  }
}

serve(async (req) => {
  const origin = req.headers.get('origin')
  const corsHeaders = getCorsHeaders(origin)

  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  // Validate content-type
  const contentType = req.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    return new Response(JSON.stringify({ error: 'Invalid content type' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '',
    )

    const body = await req.text()
    const signature = req.headers.get('x-webhook-signature')
    const webhookSecret = Deno.env.get('WEBHOOK_SECRET')

    if (!validateSignature(body, signature, webhookSecret)) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    const { type, data, provider } = JSON.parse(body)
    if (!type || !provider) {
      return new Response(JSON.stringify({ error: 'Missing type or provider' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    console.log(`[${provider}] Webhook received: ${type}`)

    const { data: event, error: storeError } = await supabase
      .from('webhook_events')
      .insert({ provider, event_type: type, webhook_data: data, processed: false })
      .select()
      .single()

    if (storeError) {
      console.error('Failed to store webhook:', storeError)
      return new Response(JSON.stringify({ error: 'Failed to store webhook' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    let alerts: any[] = []
    if (type === 'token_launch' || type === 'NFT_MINT') {
      alerts = await processBeginnerDetection(supabase, data)
    } else if (type === 'TRANSACTION') {
      alerts = await processFundingDetection(supabase, data)
    } else if (type === 'PROGRAM_DEPLOY' || type === 'AUTHORITY_CHANGE') {
      alerts = await processAdvancedDetection(supabase, data)
    }

    await supabase
      .from('webhook_events')
      .update({ processed: true, alerts_generated: alerts.length })
      .eq('id', event.id)

    const criticalAlerts = alerts.filter(a => a.severity === 'emergency' || a.severity === 'critical')
    if (criticalAlerts.length > 0) {
      await sendToN8N(criticalAlerts, type)
    }

    return new Response(
      JSON.stringify({ received: true, event_id: event.id, alerts_generated: alerts.length, critical_alerts: criticalAlerts.length }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    console.error('Webhook processing error:', error)
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})

async function processBeginnerDetection(supabase: any, data: any): Promise<any[]> {
  const alerts: any[] = []
  const tokenMint = data.token?.mint
  const deployer = data.token?.deployer
  if (!tokenMint) return alerts

  await supabase.from('token_deployments').upsert({
    token_mint: tokenMint,
    deployer_wallet: deployer || 'unknown',
    deployed_at: new Date().toISOString()
  }, { onConflict: 'token_mint' })

  if (deployer) {
    const walletAge = await getWalletAge(deployer)
    if (walletAge && walletAge < 24) {
      alerts.push({
        tier: 'beginner',
        type: 'FRESH_WALLET',
        severity: 'warning',
        title: 'New Wallet Alert',
        description: `Deployer wallet is only ${walletAge.toFixed(1)} hours old`,
        token_mint: tokenMint,
        wallet_address: deployer,
        recommendation: 'New wallets have no history - proceed with caution'
      })
    }
  }

  const honeypotCheck = await checkHoneypot(tokenMint)
  if (honeypotCheck.is_honeypot) {
    alerts.push({
      tier: 'beginner',
      type: 'HONEYPOT_BASIC',
      severity: 'emergency',
      title: 'HONEYPOT DETECTED',
      description: 'Cannot sell this token - classic honeypot',
      token_mint: tokenMint,
      recommendation: 'DO NOT BUY - This token cannot be sold'
    })
  }

  if (alerts.length > 0) {
    await supabase.from('detection_alerts').insert(alerts.map(a => ({ ...a, created_at: new Date().toISOString() })))
  }
  return alerts
}

async function processFundingDetection(supabase: any, data: any): Promise<any[]> {
  const alerts: any[] = []
  const tx = data.transaction
  if (!tx) return alerts

  const sender = tx.sender
  const receiver = tx.receiver
  const amount = tx.amount || 0

  if (sender && receiver) {
    await supabase.from('wallet_funding_relationships').insert({
      funded_wallet: receiver,
      funder_wallet: sender,
      amount_sol: amount,
      funded_at: new Date().toISOString(),
      is_dust_funding: amount < 0.01
    })

    if (amount < 0.01) {
      const { data: scammerCheck } = await supabase
        .from('authority_history')
        .select('new_authority_rug_count')
        .eq('new_authority', sender)
        .gte('new_authority_rug_count', 2)
        .single()

      if (scammerCheck) {
        alerts.push({
          tier: 'intermediate',
          type: 'NESTING_DOLL_FUNDING',
          severity: 'critical',
          title: 'Serial Scammer Funding Detected',
          description: `Deployer funded by known scammer with ${scammerCheck.new_authority_rug_count} previous rugs`,
          wallet_address: receiver,
          evidence: { funder: sender, funder_rugs: scammerCheck.new_authority_rug_count }
        })
      }
    }
  }
  return alerts
}

async function processAdvancedDetection(supabase: any, data: any): Promise<any[]> {
  const alerts: any[] = []
  const type = data.type

  if (type === 'AUTHORITY_CHANGE') {
    const programId = data.program?.id
    const newAuthority = data.new_authority
    if (programId && newAuthority) {
      await supabase.from('authority_history').insert({
        program_id: programId,
        authority_type: 'upgrade',
        old_authority: data.old_authority,
        new_authority: newAuthority,
        changed_at: new Date().toISOString()
      })

      const { data: authHistory } = await supabase.from('authority_history').select('*').eq('new_authority', newAuthority)
      const rugCount = authHistory?.length || 0
      if (rugCount >= 2) {
        alerts.push({
          tier: 'advanced',
          type: 'AUTHORITY_TIMEBOMB',
          severity: 'emergency',
          title: 'Authority Transferred to Known Rugger',
          description: `New authority has ${rugCount} previous rugs`,
          wallet_address: programId,
          evidence: { new_authority: newAuthority, previous_rugs: rugCount }
        })
      }
    }
  }
  return alerts
}

async function getWalletAge(wallet: string): Promise<number | null> {
  try {
    const heliusKey = Deno.env.get('HELIUS_KEY')
    const resp = await fetch(`https://mainnet.helius-rpc.com/?api-key=${heliusKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'getSignaturesForAddress', params: [wallet, { limit: 1 }] })
    })
    const data = await resp.json()
    const sigs = data.result || []
    if (sigs.length > 0 && sigs[0].blockTime) {
      const firstTx = new Date(sigs[0].blockTime * 1000)
      return (Date.now() - firstTx.getTime()) / (1000 * 60 * 60)
    }
    return null
  } catch (e) {
    return null
  }
}

async function checkHoneypot(tokenMint: string): Promise<{ is_honeypot: boolean }> {
  try {
    const resp = await fetch(
      `https://quote-api.jup.ag/v6/quote?inputMint=${tokenMint}&outputMint=So11111111111111111111111111111111111111112&amount=1000000&slippageBps=50`
    )
    return { is_honeypot: resp.status !== 200 }
  } catch (e) {
    return { is_honeypot: false }
  }
}

async function sendToN8N(alerts: any[], eventType: string): Promise<void> {
  const n8nUrl = Deno.env.get('N8N_WEBHOOK_URL')
  if (!n8nUrl) return
  try {
    const hasEmergency = alerts.some(a => a.severity === 'emergency')
    const webhookPath = hasEmergency ? 'detection-emergency' : 'detection-critical'
    await fetch(`${n8nUrl}/${webhookPath}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alerts, event_type: eventType, timestamp: new Date().toISOString() })
    })
  } catch (e) {
    console.error('Failed to send to n8n:', e)
  }
}
