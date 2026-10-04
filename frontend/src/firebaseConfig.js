// src/firebaseConfig.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";


// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCrdJNVgKipxoFtw-G_EuEmJ52kQGMYgZc",
  authDomain: "mittika-36f05.firebaseapp.com",
  databaseURL: "https://mittika-36f05-default-rtdb.firebaseio.com",
  projectId: "mittika-36f05",
  storageBucket: "mittika-36f05.firebasestorage.app",
  messagingSenderId: "111574296518",
  appId: "1:111574296518:web:2a07273719af8b0d9734c7"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Export auth and database
export const auth = getAuth(app);
export const db = getFirestore(app);
