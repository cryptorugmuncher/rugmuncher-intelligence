import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { contract_address, program_id } = body;

    // Support both parameter names
    const targetAddress = contract_address || program_id;

    if (!targetAddress) {
      return NextResponse.json(
        { error: 'contract_address or program_id is required' },
        { status: 400 }
      );
    }

    // Call Supabase Edge Function for contract analysis
    const response = await fetch(
      `${process.env.SUPABASE_URL}/functions/v1/contract-analyzer`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          program_id: targetAddress,
          analysis_type: 'full'
        })
      }
    );

    if (!response.ok) {
      const error = await response.text();
      console.error('Contract analyzer error:', error);
      return NextResponse.json(
        { error: 'Analysis failed', details: error },
        { status: 500 }
      );
    }

    const data = await response.json();

    // Format response for frontend
    return NextResponse.json({
      success: true,
      program_id: targetAddress,
      analysis: data.analysis,
      risk_level: data.risk_level,
      alerts: data.alerts_generated,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { error: 'Analysis failed', message: error.message },
      { status: 500 }
    );
  }
}

// Also support GET for quick status checks
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const programId = searchParams.get('program_id');

  if (!programId) {
    return NextResponse.json(
      { error: 'program_id query parameter required' },
      { status: 400 }
    );
  }

  try {
    // Fetch existing analysis from database
    const response = await fetch(
      `${process.env.SUPABASE_URL}/rest/v1/bytecode_analysis?program_id=eq.${programId}&select=*`,
      {
        headers: {
          'Authorization': `Bearer ${process.env.SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const data = await response.json();

    if (data && data.length > 0) {
      return NextResponse.json({
        success: true,
        cached: true,
        program_id: programId,
        analysis: data[0]
      });
    }

    return NextResponse.json(
      { error: 'No analysis found. Run POST to analyze.' },
      { status: 404 }
    );

  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch analysis' },
      { status: 500 }
    );
  }
}
