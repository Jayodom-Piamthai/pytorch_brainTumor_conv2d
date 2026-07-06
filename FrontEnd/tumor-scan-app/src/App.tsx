import { useState } from 'react'
import './App.css'
// import ScanImageInput from './ImageInput'

function App() {
  const [selectedImage, setSelectedImage] = useState(null); //getter setter
  const [previewUrl, setPreviewUrl] = useState('');//setter getter as string
  const [predictionResult, setPredictionResult] = useState(null);

  // const _localAPI = "http://localhost:8000/";
  const _vercelAPI = "https://pytorch-brain-tumor-conv2d.vercel.app/";
  const handleImageChange = (e:any) => { //when image is recieved,turn it into url to be use for display
    const file = e.target.files[0];
    console.log(file.type)
    if (file) {
      setSelectedImage(file);
      // Create a temporary URL for the preview
      const prevURL = URL.createObjectURL(file);
      setPreviewUrl(prevURL);
    }

  };

  // const apiTest = async () => {
  //   try{
  //      const response = await fetch('http://localhost:8000/');
  //     //  const response = await fetch('https://http.cat/');
  //      console.log(response)
  //     if (!response.ok) {
  //       throw new Error('Network response was not ok');
  //     }
  //     const result = await response.json();
  //     console.log(result)
      
  //   } catch (err) {
  //     throw new Error('Network response error!');
  //   } finally {
  //     console.log('conclude API test')
  //   }
  // };

  const tumorPrediction = async() => { 
    const formData = new FormData();
    formData.append("file", selectedImage ?? ''); // "file" must match FastAPI param name ; ?? '' for fallback null value

    const response = await fetch("/api/model/prediction", {
      method: "POST",
      body: formData,
      // DO NOT set Content-Type header — browser sets it automatically with boundary
    });

    const data = await response.json();
    setPredictionResult(data)
    return data;
  };

  const imagePrepped = selectedImage && ( //if image is selected,statement turns true and displays the div code at {imagePrepped}
    <div className='card'>
      {/* <button onClick={() => console.log("Scanning for tumor...")}> */}
      <button onClick={tumorPrediction}>
        Scan now
      </button>
    </div>
  );

  const resultRecieved = predictionResult &&(
    <div>
      <h2>{predictionResult}</h2>
    </div>
  )

  // main frontend
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
      {resultRecieved}
      {/* <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
      </div> */}
    </>
  )
}


export default App
