const fs = require('fs/promises');
const path = require('path');

const categories = ["Food", "Transport", "Utilities", "Lodging"];
const paymentMethods = ["Cash", "Credit Card", "Debit Card"];

async function sendImages() {
  const form = new FormData();

  form.append('categories', JSON.stringify(categories));
  form.append('payment_methods', JSON.stringify(paymentMethods));

  const imageNames = ['im1.jpg'];

  for (const imageName of imageNames) {
    const filePath = path.join(__dirname, imageName);

    try {
      const fileBuffer = await fs.readFile(filePath);
      const blob = new Blob([fileBuffer], { type: 'image/jpg' });
      form.append('files', blob, imageName);
    } catch (error) {
      console.warn(`Warning: Could not read ${imageName} - ${error.message}`);
    }
  }

  try {
    console.log('Sending images to FastAPI using native fetch...');

    const response = await fetch('http://localhost:8000/detect-text', {
      method: 'POST',
      body: form
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Response from server:');
    console.dir(data);

  } catch (error) {
    console.error('Error sending images:', error.message);
  }
}

sendImages();
