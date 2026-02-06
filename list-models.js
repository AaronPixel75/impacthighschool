// List all available models for this API key
const API_KEY = 'AIzaSyC7WoRW121pS2x45-F5Xv8eh6gi4ovQrZg';

async function listModels() {
    try {
        const response = await fetch(
            `https://generativelanguage.googleapis.com/v1/models?key=${API_KEY}`
        );

        const data = await response.json();

        if (response.ok && data.models) {
            console.log('✅ Available models:\n');
            data.models.forEach(model => {
                const methods = model.supportedGenerationMethods || [];
                if (methods.includes('generateContent')) {
                    console.log(`  ✓ ${model.name}`);
                    console.log(`    Display: ${model.displayName}`);
                    console.log(`    Methods: ${methods.join(', ')}\n`);
                }
            });
        } else {
            console.log('❌ Error:', data.error?.message || 'Unknown error');
        }
    } catch (err) {
        console.log('❌ Connection error:', err.message);
    }
}

listModels();
