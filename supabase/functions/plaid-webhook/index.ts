import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, content-type',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Content-Type': 'application/json',
}

serve(async (req: any) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders })
  }

  try {
    const url = new URL(req.url)
    const path = url.pathname

    // Route handling
    if (path === '/plaid/webhook') {
      return await handleWebhook(req)
    } else {
      return new Response(
        JSON.stringify({ error: 'Endpoint not found' }),
        { 
          status: 404, 
          headers: corsHeaders 
        }
      )
    }
  } catch (error: any) {
    console.error('Edge Function Error:', error)
    return new Response(
      JSON.stringify({ 
        error: error.message,
        details: error.stack 
      }),
      { 
        status: 500, 
        headers: corsHeaders 
      }
    )
  }
})

async function handleWebhook(req: any) {
  try {
    const webhookType = req.headers.get('plaid-verification')
    const body = await req.json()

    console.log('Plaid webhook received:', { webhookType, body })

    return new Response(
      JSON.stringify({ received: true }),
      { headers: corsHeaders }
    )
  } catch (error: any) {
    console.error('Webhook error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 400, 
        headers: corsHeaders 
      }
    )
  }
}