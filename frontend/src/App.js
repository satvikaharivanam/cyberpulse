import { useState } from "react";

import "./App.css";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

import {
  isLoggedIn,
  logoutUser,
} from "./services/api";


function App() {

  const [loggedIn, setLoggedIn] = useState(
    isLoggedIn()
  );

  const [showRegister, setShowRegister] =
    useState(false);


  function handleLogin() {
    setLoggedIn(true);
  }


  function handleLogout() {
    logoutUser();
    setLoggedIn(false);
  }


  if (!loggedIn) {

    if (showRegister) {

      return (
        <Register
          onSwitchToLogin={() =>
            setShowRegister(false)
          }
        />
      );

    }


    return (
      <Login
        onLogin={handleLogin}
        onSwitchToRegister={() =>
          setShowRegister(true)
        }
      />
    );

  }


  return (
    <Dashboard
      onLogout={handleLogout}
    />
  );

}


export default App;