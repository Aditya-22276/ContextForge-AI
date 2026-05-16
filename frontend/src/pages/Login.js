import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";

function Login() {

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const navigate = useNavigate();


//Normal Login
  const handleLogin = async () => {

    try {

      const res = await fetch(
        "http://127.0.0.1:8000/api/login",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            email,
            password
          })
        }
      );

      const data = await res.json();

      if (res.ok) {

        localStorage.setItem(
          "token",
          data.access_token
        );

        navigate("/");

      } else {

        alert(
          data.detail || "Login failed"
        );

      }

    } catch (err) {

      console.error(err);

      alert("Error logging in");

    }

  };


  
  // GOOGLE LOGIN
  
  const handleGoogleLogin = async (
    credentialResponse
  ) => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/api/google-login",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            token:
              credentialResponse.credential,
          }),
        }
      );

      const data =
        await response.json();

      if (response.ok) {

        localStorage.setItem(
          "token",
          data.access_token
        );

        navigate("/");

      } else {

        alert(
          data.detail ||
          "Google login failed"
        );

      }

    } catch (err) {

      console.error(err);

      alert("Google login error");

    }

  };


  return (

    <div className="auth-container">

     <h2 style={{ color: "red" }}>
  THIS IS REAL LOGIN
</h2>


      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) =>
          setEmail(e.target.value)
        }
      />


      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) =>
          setPassword(e.target.value)
        }
      />


      <button onClick={handleLogin}>
        Login
      </button>

      <div
  style={{
    background: "white",
    color: "black",
    padding: "20px",
    marginTop: "20px"
  }}
>
  TEST GOOGLE AREA
</div>


      {/* GOOGLE LOGIN */}

     <div className="google-login-wrapper">

        <GoogleLogin
          onSuccess={handleGoogleLogin}

          onError={() => {

            console.log(
              "Google Login Failed"
            );

          }}
        />

      </div>


      <p
        onClick={() =>
          navigate("/register")
        }

        style={{
          marginTop: "20px",
          cursor: "pointer"
        }}
      >

        Don't have an account?
        Register

      </p>

    </div>

  );

}

export default Login;