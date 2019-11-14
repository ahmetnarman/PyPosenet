import * as posenet from '@tensorflow-models/posenet';
import * as tf from '@tensorflow/tfjs';
// for visualization purposes
import {
  drawBoundingBox,
  drawKeypoints,
  drawSkeleton,
  renderImageToCanvas,
} from './demo_util';

// Used if you want to render the images with overlaid keypoints on browser
async function renderPose(imageElement, net){

  var canvasElement = document.getElementById('myCanvas');

  var poses = await net.estimateSinglePose(imageElement, {
    flipHorizontal: false,
    maxDetections: 2,
    scoreThreshold: 0.6,
    nmsRadius: 20});

  renderImageToCanvas(imageElement, [imageElement.width, imageElement.height], canvasElement)
  const ctx = canvasElement.getContext('2d');
  drawKeypoints(poses.keypoints, 0.1, ctx);
  drawSkeleton(poses.keypoints, 0.5, ctx);
  drawBoundingBox(poses.keypoints, ctx);
  return poses;
}

// Used if you just want to get the keypoints without rendering
async function getPose(imageElement, net){

  var canvasElement = document.getElementById('myCanvas');

  var poses = await net.estimateSinglePose(imageElement, {
    flipHorizontal: false,
    maxDetections: 2,
    scoreThreshold: 0.6,
    nmsRadius: 20});

  return poses;
}

async function run(){
  var i=1;
  var nextImage = true;
  var pose;
  var poseArray = [];
  var fileName = window.location.pathname.split('/').pop();
  let net;
  console.log(fileName);

  // Selecting the model based on the user preference
  if (fileName == 'video_M1.html'){
    net = await posenet.load({
      architecture: 'MobileNetV1',
      outputStride: 16,
      inputResolution: 257,
      multiplier: 0.5,
      quantBytes: 2});
  } else if (fileName =='video_M2.html'){
    net = await posenet.load({
      architecture: 'MobileNetV1',
      outputStride: 8,
      inputResolution: 513,
      multiplier: 1,
      quantBytes: 2});
  } else if (fileName == 'video_R1.html') {
    net = await posenet.load({
      architecture: 'ResNet50',
      outputStride: 32,
      inputResolution: 257,
      quantBytes: 2});
  } else if (fileName == 'video_R2.html') {
    net = await posenet.load({
      architecture: 'ResNet50',
      outputStride: 16,
      inputResolution: 513,
      quantBytes: 2});
  }
  console.log(net)
  while (nextImage){
    var imageElement = document.getElementById('input'+i);
    if (imageElement != null){
      var t0 = performance.now();
      pose = await renderPose(imageElement, net);
      var t1 = performance.now();
      console.log('Estimation time:'+((t1-t0)/1000))
      poseArray.push(pose)
      i++;
    } else {
      nextImage = false;
    }
  }
  console.log(poseArray);
  net.dispose();
  var jsonData = JSON.stringify(poseArray);

  // To download the detected keypoints, use this function
  function download(content, fileName, contentType) {
    var a = document.createElement("a");
    var file = new Blob([content], {type: contentType});
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
  }
  download(jsonData, 'json.txt', 'text/plain');

}

console.log('Came this far, yay!');
run();
