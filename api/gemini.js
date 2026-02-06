export const config = {
    runtime: 'edge', // Use Edge Runtime for faster performance
};

export default async function handler(req) {
    // Only allow POST requests
    if (req.method !== 'POST') {
        return new Response(JSON.stringify({ error: 'Method not allowed' }), {
            status: 405,
            headers: { 'Content-Type': 'application/json' },
        });
    }

    try {
        const { prompt } = await req.json();

        // Get the API key from environment variables
        const API_KEY = process.env.GEMINI_API_KEY || process.env.apikey || process.env.APIKEY;

        if (!API_KEY) {
            return new Response(JSON.stringify({ error: 'Server configuration error: Missing API Key' }), {
                status: 500,
                headers: { 'Content-Type': 'application/json' },
            });
        }

        // List of models to try (in order of preference/cost)
        const models = [
            'gemini-2.5-flash-lite',
            'gemini-2.0-flash-lite',
            'gemini-2.5-flash',
            'gemini-2.0-flash'
        ];

        let lastError = null;
        let successfulResponse = null;

        // Try each model until one works
        for (const model of models) {
            try {
                // console.log(`Attempting model: ${model}`); // Optional debugging
                const response = await fetch(
                    `https://generativelanguage.googleapis.com/v1/models/${model}:generateContent?key=${API_KEY}`,
                    {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            contents: [{
                                parts: [{
                                    text: "You are a helpful school tutor. Context: High School. Keep answers concise and encouraging. Question: " + prompt
                                }]
                            }]
                        })
                    }
                );

                const data = await response.json();

                if (response.ok && data.candidates?.[0]?.content?.parts?.[0]?.text) {
                    successfulResponse = data.candidates[0].content.parts[0].text;
                    break; // Success! Stop looping.
                } else {
                    // Capture specific error to help with fallback logic or final reporting
                    const errorMsg = data.error?.message || response.statusText;
                    lastError = `Model ${model} failed: ${errorMsg}`;
                    // Continue to next model...
                }

            } catch (err) {
                lastError = `Model ${model} connection error: ${err.message}`;
            }
        }

        if (successfulResponse) {
            return new Response(JSON.stringify({ text: successfulResponse }), {
                status: 200,
                headers: { 'Content-Type': 'application/json' },
            });
        }

        // If we exhausted all models
        throw new Error(lastError || "All AI models failed to respond.");

    } catch (error) {
        console.error("API Error:", error);
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' },
        });
    }
}
