import { useState } from 'react'
import './App.css'
// import ScanImageInput from './ImageInput'


// function imageScanAPI(image){
//   const [message, setMessage] = useState('');
//    try {
//       const response = await fetch('http://localhost:8000/items/', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: image,
//       });

//       if (!response.ok) {
//         throw new Error('Network response was not ok');
//       }

//       const data = await response.json();
//       setMessage(data.message);
//     } catch (error) {
//       setMessage('Error sending data: ' + error.message);
//     }
//   };
// }

function App() {
  const [selectedImage, setSelectedImage] = useState(null); //getter setter
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    console.log(file.type)
    if (file) {
      setSelectedImage(file);
      // Create a temporary URL for the preview
      setPreviewUrl(URL.createObjectURL(file));
    }

  };

  const apiTest = async () => {
    try{
       const response = await fetch('http://localhost:8000/');
      //  const response = await fetch('https://http.cat/');
       console.log(response)
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      // const result = await response.json();
      
    } catch (err) {
      throw new Error('Network response error!');
    } finally {
      console.log('conclude API test')
    }
  }

  const imagePrepped = selectedImage && (
    <div className='card'>
      {/* <button onClick={() => console.log("Scanning for tumor...")}> */}
      <button onClick={apiTest}>
        Scan now
      </button>
    </div>
  );

  return (
    <>
      <h1>Brain Tumor Scanner</h1>
      <div className='imageInput'>
        <input 
          type="file" 
          accept="image/*" // Restricts file picker to images
          onChange={handleImageChange} 
        />
      </div>
      {/* <div>
        <ImageInput source="pictures" label="Related pictures">
            <ImageField source="src" title="title" />
        </ImageInput>
      </div> */}
      <div>
        {previewUrl && (
          <img 
            src={previewUrl} 
            alt="Preview" 
            style={{ width: '200px', marginTop: '10px' }} 
          />
        )}
      </div>
      {imagePrepped}
      {/* <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
      </div> */}
    </>
  )
}


export default App
