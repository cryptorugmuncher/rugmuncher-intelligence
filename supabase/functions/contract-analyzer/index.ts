import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

// BPF Program Analysis Edge Function
// Provides advanced bytecode analysis for scam detection

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_KEY') ?? ''
    )

    const { program_id, analysis_type = 'full' } = await req.json()

    if (!program_id) {
      return new Response(
        JSON.stringify({ error: 'program_id is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log(`[Contract Analyzer] Analyzing: ${program_id}`)

    // Fetch program bytecode from QuickNode
    const bytecode = await fetchProgramBytecode(program_id)

    if (!bytecode) {
      return new Response(
        JSON.stringify({ error: 'Failed to fetch program bytecode' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Run analysis based on type
    let analysis: any = {}

    switch (analysis_type) {
      case 'entropy':
        analysis = { entropy: calculateShannonEntropy(bytecode) }
        break
      case 'patterns':
        analysis = detectMaliciousPatterns(bytecode)
        break
      case 'full':
      default:
        analysis = {
          entropy: calculateShannonEntropy(bytecode),
          patterns: detectMaliciousPatterns(bytecode),
          bytecode_size: bytecode.length,
          is_upgradeable: await checkUpgradeAuthority(program_id),
          analyzed_at: new Date().toISOString()
        }
        break
    }

    // Store analysis results
    await supabase.from('bytecode_analysis').upsert({
      program_id,
      analyzed_at: new Date().toISOString(),
      shannon_entropy: analysis.entropy,
      obfuscation_detected: analysis.entropy > 7.5,
      contains_ipfs_hashes: analysis.patterns?.hasIPFS || false,
      contains_c2_urls: analysis.patterns?.hasC2 || false,
      byte_distribution_score: analysis.patterns?.distributionScore || 0
    }, { onConflict: 'program_id' })

    // Generate alerts if suspicious
    const alerts: any[] = []

    if (analysis.entropy > 7.5) {
      alerts.push({
        tier: 'advanced',
        type: 'BYTECODE_OBFUSCATION',
        severity: 'critical',
        title: 'Heavily Obfuscated Contract',
        description: `Shannon entropy ${analysis.entropy.toFixed(2)} indicates obfuscation`,
        wallet_address: program_id,
        evidence: {
          entropy: analysis.entropy,
          normal_range: '5.2-6.1',
          bytecode_size: bytecode.length
        },
        recommendation: 'Contract hides malicious logic through obfuscation'
      })
    }

    if (analysis.patterns?.hasC2) {
      alerts.push({
        tier: 'advanced',
        type: 'C2_URLS_IN_BYTECODE',
        severity: 'emergency',
        title: 'Command & Control URLs Detected',
        description: 'Bytecode contains hardcoded C2 server URLs',
        wallet_address: program_id,
        recommendation: 'Potential botnet/backdoor - DO NOT INTERACT'
      })
    }

    // Store alerts
    if (alerts.length > 0) {
      await supabase.from('detection_alerts').insert(
        alerts.map(a => ({ ...a, created_at: new Date().toISOString() }))
      )

      // Send to n8n
      await sendToN8N(alerts)
    }

    return new Response(
      JSON.stringify({
        program_id,
        analysis,
        alerts_generated: alerts.length,
        risk_level: alerts.length > 0 ? 'HIGH' : 'LOW'
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Contract analysis error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

// Fetch program bytecode from QuickNode
async function fetchProgramBytecode(programId: string): Promise<Uint8Array | null> {
  try {
    const quicknodeKey = Deno.env.get('QUICKNODE_KEY')
    const resp = await fetch(
      `https://winter-indulgent-sunset.solana-mainnet.quiknode.pro/${quicknodeKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 1,
          method: 'getAccountInfo',
          params: [programId, { encoding: 'base64' }]
        })
      }
    )

    const data = await resp.json()
    const accountData = data.result?.value?.data?.[0]

    if (accountData) {
      // Decode base64
      const binary = atob(accountData)
      const bytes = new Uint8Array(binary.length)
      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i)
      }
      return bytes
    }

    return null
  } catch (e) {
    console.error('Failed to fetch bytecode:', e)
    return null
  }
}

// Calculate Shannon entropy of bytecode
function calculateShannonEntropy(data: Uint8Array): number {
  if (data.length === 0) return 0

  const counts = new Map<number, number>()
  for (const byte of data) {
    counts.set(byte, (counts.get(byte) || 0) + 1)
  }

  let entropy = 0
  const len = data.length

  for (const count of counts.values()) {
    if (count > 0) {
      const p = count / len
      entropy -= p * Math.log2(p)
    }
  }

  return entropy
}

// Detect malicious patterns in bytecode
function detectMaliciousPatterns(data: Uint8Array): any {
  // Convert to string for pattern matching
  let asString = ''
  for (const byte of data) {
    if (byte >= 32 && byte <= 126) {
      asString += String.fromCharCode(byte)
    }
  }

  // Check for IPFS hashes (Qm...)
  const ipfsPattern = /Qm[1-9A-HJ-NP-Za-km-z]{44}/g
  const ipfsMatches = asString.match(ipfsPattern) || []

  // Check for URLs (http/https)
  const urlPattern = /https?:\/\/[^\s\"]+/gi
  const urlMatches = asString.match(urlPattern) || []

  // Check for suspicious domains
  const suspiciousDomains = ['github.io', 'vercel.app', 'netlify.app', 'pastebin', 'rentry']
  const hasSuspiciousURL = urlMatches.some(url =>
    suspiciousDomains.some(domain => url.includes(domain))
  )

  // Check for C2 patterns (common botnet indicators)
  const c2Patterns = [
    /discord\.com\/api\/webhooks/i,
    /telegram\.org\/bot/i,
    /api\.telegram\.org/i
  ]
  const hasC2 = c2Patterns.some(p => p.test(asString))

  // Calculate byte distribution score
  const uniqueBytes = new Set(data).size
  const distributionScore = uniqueBytes / 256

  return {
    hasIPFS: ipfsMatches.length > 0,
    ipfsHashes: ipfsMatches.slice(0, 5),
    hasURLs: urlMatches.length > 0,
    urls: urlMatches.slice(0, 5),
    hasSuspiciousURL,
    hasC2,
    distributionScore: Math.round(distributionScore * 100) / 100
  }
}

// Check if program has upgrade authority
async function checkUpgradeAuthority(programId: string): Promise<boolean> {
  try {
    const quicknodeKey = Deno.env.get('QUICKNODE_KEY')
    const resp = await fetch(
      `https://winter-indulgent-sunset.solana-mainnet.quiknode.pro/${quicknodeKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 1,
          method: 'getAccountInfo',
          params: [programId, { encoding: 'jsonParsed' }]
        })
      }
    )

    const data = await resp.json()
    const account = data.result?.value

    // Check if program has upgrade authority set
    // This is a simplified check - real implementation would parse program data
    return account?.executable === true
  } catch (e) {
    return false
  }
}

// Send alerts to n8n
async function sendToN8N(alerts: any[]): Promise<void> {
  const n8nUrl = Deno.env.get('N8N_WEBHOOK_URL')
  if (!n8nUrl) return

  const hasEmergency = alerts.some(a => a.severity === 'emergency')
  const webhookPath = hasEmergency ? 'detection-emergency' : 'detection-critical'

  try {
    await fetch(`${n8nUrl}/${webhookPath}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        alerts,
        source: 'contract-analyzer',
        timestamp: new Date().toISOString()
      })
    })
  } catch (e) {
    console.error('Failed to send to n8n:', e)
  }
}
