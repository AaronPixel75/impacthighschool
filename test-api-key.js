// Quick test to see which models work with your API key
const API_KEY = 'AIzaSyC7WoRW121pS2x45-F5Xv8eh6gi4ovQrZg';

const models = [
    'gemini-1.5-flash-latest',
    'gemini-1.5-pro-latest',
    'gemini-pro',
    'gemini-1.5-flash',
    'gemini-1.5-pro'
];

async function testModels() {
    console.log('Testing models with your API key...\n');

    for (const model of models) {
        try {
            const response = await fetch(
                `https://generativelanguage.googleapis.com/v1/models/${model}:generateContent?key=${API_KEY}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        contents: [{
                            parts: [{ text: "Say hello" }]
                        }]
                    })
                }
            );

            const data = await response.json();

            if (response.ok && data.candidates?.[0]?.content?.parts?.[0]?.text) {
                console.log(`✅ ${model}: WORKS!`);
                console.log(`   Response: ${data.candidates[0].content.parts[0].text}\n`);
            } else {
                console.log(`❌ ${model}: ${data.error?.message || 'Unknown error'}\n`);
            }
        } catch (err) {
            console.log(`❌ ${model}: ${err.message}\n`);
        }
    }
}

testModels();
