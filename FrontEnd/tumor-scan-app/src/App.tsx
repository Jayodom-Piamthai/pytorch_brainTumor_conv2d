import { useState } from 'react'
import './App.css'
// import ScanImageInput from './ImageInput'


function adaptiveResult(result:string){
  console.log(result)
  switch(result){
    case "notumor":
      return(
        <div>
          <h2>No tumor</h2>
          <h3>model detected no tumor inside MRI scan image</h3>
        </div>
      )
    case "meningioma":
      return(
        <div>
          <h2>"Meningioma tumor"</h2>
          <h3>
            starts in the meninges region of the brain close to the spinal chord,
            the most common type of brain tumor  grow slowly. Some cause no symptoms for many years.
            When they get bigger or sit near important areas,they can lead to serious health conditions
          </h3>
          <h2>Symptoms:</h2>
          <h3>
            Changes in vision(such as blurriness or double vision).
            Numbness, tingling, pain or weakness on one side of the face.
            Headaches that are worse in the morning or change over time.
            Hearing loss or ringing in one ear.
            Loss of smell.
            Seizures.
            Weakness or numbness in the arms or legs on one side of the body.
          </h3>
        </div>
      )
    case "glioma":
      return(
        <div>
          <h2>"Glioma tumor"</h2>
          <h3>
            forms when your body’s glial cells which support nerves and central nervous system near spinal chord
            grow out of control. gliomas can grow quickly and can invade healthy brain tissue.

          </h3>
          <h2>Symptoms:</h2>
          <h3>
            Changes in your vision or sudden vision loss.
            Difficulty walking or keeping your balance
            Dizziness,
            Headaches,
            Nausea and vomiting,
            New depression or anxiety,
            Personality changes or sudden mood swings,
            Seizures,
            Trouble speaking or communicating (aphasia),
            Trouble thinking, learning or remembering (cognitive problems),
            Weakness or numbness on one side of your body (hemiparesis),
          </h3>
        </div>
      )
    case "pituitary":
      return(
        <div>
          <h2>"Pituitary tumor"</h2>
          <h3>
            this tumor are growths that form in the pituitary gland located behind the nose at the base of the brain
            which makes hormones that help control many important body functions including  sends chemical messages that tell other glands 
            in the body when to start or stop making their hormones. they grow slowly. They do not spread to other parts of the body.
            but have a chance to become aggressive and cancerous
          </h3>
          <h2>Symptoms:</h2>
          <h3>
            Headache.
            Vision issues, especially loss of side vision and double vision.
            Facial numbness or pain.
            Drooping eyelid.
            Seizures.
          </h3>
        </div>
      )
    default:
      return(
        <h2>what????</h2>
      )
  }
}

function App() {
  const [selectedImage, setSelectedImage] = useState(null); //getter setter
  const [previewUrl, setPreviewUrl] = useState('');//setter getter as string
  const [predictionResult, setPredictionResult] = useState('');
  const _localAPI = import.meta.env.VITE_API_URL || "http://localhost:8000/"; //import for railway too
  // const _vercelAPI = "https://pytorch-brain-tumor-conv2d.vercel.app/";
  const handleImageChange = (e:any) => { //when image is recieved,turn it into url to be use for display
    const file = e.target.files[0];
    console.log(file.type)
    if (file) {
      setSelectedImage(file);
      // Create a temporary URL for the preview
      const prevURL = URL.createObjectURL(file);
      console.log(prevURL);
      setPreviewUrl(prevURL);
    }

  };
  // const resultJsonSchema = z.object({
  //   detectionImage:z.string(),
  //   resultName:z.string(),
  // });

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

    // const response = await fetch("/api/model/prediction", {
    const response = await fetch(_localAPI + "model/prediction", {
      method: "POST",
      body: formData,
      // DO NOT set Content-Type header — browser sets it automatically with boundary
    });

    const data = await response.json();
    setPredictionResult(data)
    return data;
  };

  const YoloTumorPrediction = async() => { 
    const formData = new FormData();
    formData.append("file", selectedImage ?? ''); // "file" must match FastAPI param name ; ?? '' for fallback null value

    // const response = await fetch("/api/model/prediction", {
    const response = await fetch(_localAPI + "model/YOLOprediction", {
      method: "POST",
      body: formData,
      // DO NOT set Content-Type header — browser sets it automatically with boundary
    });

    // const data = await resultJsonSchema.parse( response.json() );
    const data = await response.json();
    setPredictionResult(data.resultName)
    const predictedImage = atob(data.detectionImage);
    fetch(`data:image/png;base64,${data.detectionImage}`)
    .then(res => res.blob())
    .then(blob => {
      const fileUrl = URL.createObjectURL(blob);
      setPreviewUrl(fileUrl)
      console.log("Binary file ready at:", fileUrl);
    });
    console.log(typeof(predictedImage))
    handleImageChange(predictedImage)
    return data.resultName;
  };


  const imagePrepped = selectedImage && ( //if image is selected,statement turns true and displays the div code at {imagePrepped}
    <div className='card'>
      {/* <button onClick={() => console.log("Scanning for tumor...")}> */}
      {/* <button onClick={tumorPrediction}>
        Scan now
      </button> */}
      <button onClick={YoloTumorPrediction}>
        Scan now 
      </button>
    </div>
  );

  const resultRecieved = predictionResult ? (
    <div className='diagBox'>
      {/* <h2>{predictionResult}</h2> */}
      <div>{adaptiveResult(predictionResult)}</div>
    </div>
  ) :
  (
    <div className='diagBox'>
      <h2>[prediction result and diagnostic will appear here]</h2>
    </div>
  )

  // main frontend
  return (
    <>
      <h1 className='head'>Brain Tumor Scanner</h1>
      <div className='rowBox'>
        <div className="subBox">
          <div className='imageInput'>
            <input 
              type="file" 
              accept="image/*" // Restricts file picker to images
              onChange={handleImageChange} 
            />
          </div>
          <div>
            {previewUrl && (
              <img 
              src={previewUrl} 
              alt="Preview" 
              style={{ maxHeight: '21vw', maxWidth: '30vw', margin:'1vw' , borderRadius:'1vw' }} 
              />
            )}
          </div>
          {imagePrepped}
        </div>
        <div className="subBox">
          {resultRecieved}
        </div>
      </div>
      {/* <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
      </div> */}
    </>
  )
}


export default App
