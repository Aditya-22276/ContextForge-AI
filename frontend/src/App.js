import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";
import { GoogleLogin } from "@react-oauth/google";

function App() {

  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);

  const [, setChatHistory] = useState([]);
  const [sessions, setSessions] = useState([]);

  const [currentSessionId, setCurrentSessionId] = useState(null);

  const [isTyping, setIsTyping] = useState(false);

  const [docText, setDocText] = useState("");

  const [selectedFile, setSelectedFile] = useState(null);

  const [dragActive, setDragActive] = useState(false);

const [documents, setDocuments] = useState([]);

  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const [isRegister, setIsRegister] = useState(false);

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const chatEndRef = useRef(null);

  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState(

  localStorage.getItem("theme") || "dark"

);

  // AUTO SCROLL
  useEffect(() => {

    chatEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });

  }, [messages, isTyping]);

  useEffect(() => {

  document.body.className = theme;

  localStorage.setItem(
    "theme",
    theme
  );

}, [theme]);

  // HANDLE GOOGLE OAUTH REDIRECT
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const oauthToken = params.get("token");
    if (oauthToken) {
      localStorage.setItem("token", oauthToken);
      // Clean token from URL
      window.history.replaceState({}, document.title, window.location.pathname);
      setIsLoggedIn(true);
      setTimeout(() => {
        fetchDocuments();
        fetchChatHistory();
        fetchSessions();
      }, 100);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // CHECK TOKEN
  useEffect(() => {

    const token = localStorage.getItem("token");

    if (!token) return;

    setIsLoggedIn(true);

    setTimeout(() => {

      fetchDocuments();
      fetchChatHistory();
      fetchSessions();

    }, 100);

  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // FETCH DOCUMENTS
  const fetchDocuments = async () => {

    const token = localStorage.getItem("token");

    if (!token) return;

    try {

      const res = await fetch(
        "http://127.0.0.1:8000/api/documents",
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      // FIX 401
      if (res.status === 401) {

        localStorage.removeItem("token");

        setIsLoggedIn(false);

        return;

      }

      const data = await res.json();

      if (Array.isArray(data)) {

        setDocuments(data);

      } else {

        setDocuments([]);

      }

    } catch (err) {

      console.log(err);

    }

  };

  // FETCH CHAT HISTORY
  const fetchChatHistory = async () => {

    try {

      const token = localStorage.getItem("token");

      if (!token) return;

      const res = await fetch(
        "http://127.0.0.1:8000/api/history",
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      // FIX 401
      if (res.status === 401) {

        localStorage.removeItem("token");

        setIsLoggedIn(false);

        return;

      }

      const data = await res.json();

      setChatHistory(data);

    } catch (err) {

      console.log(err);

    }

  };

  // FETCH SESSIONS
const fetchSessions = async () => {

  try {

    const token =
      localStorage.getItem("token");

    const res = await fetch(

      "http://127.0.0.1:8000/api/sessions",

      {
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      }
    );

    const data =
      await res.json();

    // SAFETY CHECK
    if (Array.isArray(data)) {

      setSessions(data);

    } else {

      setSessions([]);

    }

  } catch (err) {

    console.log(err);

    setSessions([]);

  }

};

// LOAD SESSION CHATS
const loadSessionChats = async (sessionId) => {

  try {

    const token = localStorage.getItem("token");

    const res = await fetch(
      `http://127.0.0.1:8000/api/history/${sessionId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );

    const data = await res.json();

    const formattedMessages = [];

    data.forEach((chat) => {

      formattedMessages.push({
        role: "user",
        text: chat.question
      });

      formattedMessages.push({
        role: "bot",
        text: chat.answer,
       sources: chat.sources || []
      });

    });

    setMessages(formattedMessages);

    setCurrentSessionId(sessionId);

  } catch (err) {

    console.log(err);

  }

};

  // DELETE DOCUMENT
  const deleteDocument = async (filename) => {

    const token = localStorage.getItem("token");

    try {

      await fetch(
        `http://127.0.0.1:8000/api/documents/${filename}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      fetchDocuments();

    } catch (err) {

      console.log(err);

    }

  };

  // LOGIN
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

      if (data.access_token) {

        localStorage.setItem(
          "token",
          data.access_token
        );

        setIsLoggedIn(true);

        fetchDocuments();

        fetchChatHistory();
        fetchSessions();

        alert("Login successful ✅");

      } else {

        alert(
          data.detail ||
          "Login failed ❌"
        );

      }

    } catch (err) {

      console.log(err);

      alert("Server error ❌");

    }

  };

  // REGISTER
  const handleRegister = async () => {

    try {

      const res = await fetch(
        "http://127.0.0.1:8000/api/register",
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

      if (data.message) {

        alert(
          "Registered successfully ✅"
        );

        setIsRegister(false);

      } else {

        alert(
          data.detail ||
          "Registration failed ❌"
        );

      }

    } catch (err) {

      console.log(err);

      alert("Server error ❌");

    }

  };

  // GOOGLE LOGIN
  const handleGoogleLogin = async (credentialResponse) => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/api/google-login",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            token: credentialResponse.credential,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {

        localStorage.setItem("token", data.access_token);

        setIsLoggedIn(true);

        fetchDocuments();
        fetchChatHistory();
        fetchSessions();

      } else {

        alert(data.detail || "Google login failed");

      }

    } catch (err) {

      console.error(err);

      alert("Google login error");

    }

  };

  // LOGOUT
  const handleLogout = () => {

    localStorage.removeItem("token");

    setIsLoggedIn(false);

    setMessages([]);

    setDocuments([]);

    setChatHistory([]);

    setSessions([]);

    setCurrentSessionId(null);

    alert("Logged out successfully");

  };

  // UPLOAD
  const handleUpload = async () => {

    const token = localStorage.getItem("token");

    if (!token) {

      alert("Please login first ❗");

      return;

    }

    try {

      // FILE UPLOAD
      if (selectedFile) {

        const formData = new FormData();

        formData.append(
          "file",
          selectedFile
        );

        const res = await fetch(
          "http://127.0.0.1:8000/api/upload-file",
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`
            },
            body: formData
          }
        );

        const data = await res.json();

        if (!res.ok) {

          alert(
            data.detail ||
            "Upload failed ❌"
          );

          return;

        }

        alert(
          "File uploaded successfully ✅"
        );

        fetchDocuments();

        setSelectedFile(null);

        setDocText("");

        return;

      }

      // TEXT UPLOAD
      if (!docText.trim()) {

        alert(
          "Enter or upload document ❗"
        );

        return;

      }

      const formData = new FormData();

      formData.append(
        "content",
        docText
      );

      const res = await fetch(
        "http://127.0.0.1:8000/api/upload",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`
          },
          body: formData
        }
      );

      const data = await res.json();

      if (!res.ok) {

        alert(
          data.detail ||
          "Upload failed ❌"
        );

        return;

      }

      alert(
        "Text uploaded successfully ✅"
      );

      fetchDocuments();

      setDocText("");

    } catch (err) {

      console.log(err);

      alert("Upload failed ❌");

    }

  };

  // DRAG EVENTS
  const handleDrag = (e) => {

    e.preventDefault();

    e.stopPropagation();

    if (
      e.type === "dragenter" ||
      e.type === "dragover"
    ) {

      setDragActive(true);

    } else if (e.type === "dragleave") {

      setDragActive(false);

    }

  };

  const handleDrop = (e) => {

    e.preventDefault();

    e.stopPropagation();

    setDragActive(false);

    if (
      e.dataTransfer.files &&
      e.dataTransfer.files[0]
    ) {

      setSelectedFile(
        e.dataTransfer.files[0]
      );

    }

  };

  // CHAT
  const handleChat = async () => {

    if (!query.trim()) return;

    const token = localStorage.getItem("token");

    if (!token) {

      alert("Please login first ❗");

      return;

    }

    const currentQuery = query;

    // USER MESSAGE
    const updatedMessages = [
      ...messages,
      {
        role: "user",
        text: currentQuery
      }
    ];

    setMessages(updatedMessages);

    setQuery("");

    setIsTyping(true);
    setLoading(true);

    try {

      // API CALL
      const res = await fetch(
        "http://127.0.0.1:8000/api/chat",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",

            Authorization:
              `Bearer ${token}`
          },

          body: JSON.stringify({

          query: currentQuery,

          history: updatedMessages,

          session_id: currentSessionId

})
        }
      );

    const data = await res.json();

setMessages(prev => [
  ...prev,
  {
    role: "bot",
    text: data.answer || "No response generated.",
    sources: data.sources || []
  }
]);

fetchSessions();

setIsTyping(false);
setLoading(false);

    } catch (err) {

      console.log(err);

      setMessages(prev => [
        ...prev,
        {
          role: "bot",
          text: "Server error ❌"
        }
      ]);

      setIsTyping(false);
      setLoading(false);

    }

  };

  // LOGIN SCREEN
  if (!isLoggedIn) {

    return (

      <div className="auth-wrapper">

        <div className="auth-box">

          <h1>ContextForge AI</h1>

          <h2>
            {isRegister
              ? "Create Account"
              : "Welcome Back"}
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

          {isRegister ? (

            <button onClick={handleRegister}>
              Register
            </button>

          ) : (

            <button onClick={handleLogin}>
              Login
            </button>

          )}

          <div className="auth-divider">
            <span>or</span>
          </div>

          <div className="google-login-wrapper">
            <GoogleLogin
              onSuccess={handleGoogleLogin}
              onError={() => {
                console.log("Google Login Failed");
              }}
            />
          </div>

          <p
            onClick={() =>
              setIsRegister(!isRegister)
            }
          >

            {isRegister
              ? "Already have an account? Login"
              : "Don't have an account? Register"}

          </p>

        </div>

      </div>
    );

  }

  return (

    <div className="app">

      {/* SIDEBAR */}
      <div className="sidebar">

        <div className="logo">

          <div className="logo-icon">
            ✦
          </div>

          <span>
            ContextForge AI
          </span>

        </div>

        <div className="status-box">
          🟢 Logged In
        </div>

        <div className="theme-switch">

  <span>
    {theme === "dark"
      ? "🌙"
      : "☀️"}
  </span>

  <label className="switch">

    <input
      type="checkbox"

      checked={theme === "light"}

      onChange={() =>

        setTheme(
          theme === "dark"
            ? "light"
            : "dark"
        )

      }
    />

    <span className="slider"></span>

  </label>

</div>


        

        <button
          className="new-chat"
          onClick={handleLogout}
        >
          Logout
        </button>
        <button
  className="new-chat-btn"
  onClick={() => {

    setMessages([]);

    setCurrentSessionId(null);

  }}
>

  + New Chat

</button>

        {/* UPLOAD */}
        <div
          className={`upload-box ${
            dragActive ? "drag-active" : ""
          }`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
        >

          <textarea
            placeholder="Paste your document here..."
            value={docText}
            onChange={(e) =>
              setDocText(e.target.value)
            }
          />

          {/* FILE INPUT */}
          <div className="file-upload-wrapper">

            <label className="custom-file-upload">

              📁 Choose File

              <input
                type="file"
                accept=".txt,.pdf"
                onChange={(e) =>
                  setSelectedFile(
                    e.target.files[0]
                  )
                }
                hidden
              />

            </label>

            {selectedFile && (

              <div className="selected-file">

                <span>
                  📄 {selectedFile.name}
                </span>

                <button
                  type="button"
                  className="remove-file"
                  onClick={() =>
                    setSelectedFile(null)
                  }
                >
                  ✕
                </button>

              </div>

            )}

          </div>

          <button
            className="upload-btn"
            onClick={handleUpload}
          >
            Upload Document
          </button>

        </div>

        {/* DOCUMENTS */}
        {documents.length > 0 && (
          <div className="documents-section">
            <h2 className="history-title">Documents</h2>
            {documents.map((doc) => (
              <div key={doc.filename} className="session-item">
                <div>📄 {doc.filename}</div>
                <button onClick={() => deleteDocument(doc.filename)}>✕</button>
              </div>
            ))}
          </div>
        )}

        {/* HISTORY */}
        <div className="documents-section">

          <h2 className="history-title">
            Chat History
          </h2>

          <div className="history-list">

         {sessions.map((session) => (

  <div
    key={session.id}
    className={
      currentSessionId === session.id
        ? "session-item active-session"
        : "session-item"
    }
    
  >

    <div
      onClick={() =>
        loadSessionChats(session.id)
      }
      
    >
      📁 {session.title}
    </div>

    <button
      onClick={async (e) => {

        e.stopPropagation();

        const token =
          localStorage.getItem("token");

        await fetch(
          `http://127.0.0.1:8000/api/sessions/${session.id}`,
          {
            method: "DELETE",
            headers: {
              Authorization:
                `Bearer ${token}`
            }
          }
        );

        fetchSessions();

        if (
          currentSessionId === session.id
        ) {

          setMessages([]);

          setCurrentSessionId(null);

        }

      }}

      
    >
      ✕
    </button>

  </div>

))}

        </div>

      </div>

      </div>

      {/* CHAT */}
      <div className="chat-container">

        <div className="chat-header">
          <h2>ContextForge AI</h2>
        </div>

        <div className="chat-body">

          {messages.map((msg, i) => (

            <div
              key={i}
              className={`message-row ${msg.role}`}
            >

              {msg.role === "bot" && (
                <div className="avatar">
                  ✦
                </div>
              )}

              
 <div className={`message ${msg.role}`}>

  <ReactMarkdown>
    {msg.text || ""}
  </ReactMarkdown>

  {/* SOURCES */}
    {msg.role === "bot" &&
    msg.sources &&
    msg.sources.length > 0 && (

      <div className="sources-box">

        <div className="sources-title">
          📚 Sources
        </div>

        {msg.sources.map((source, index) => (

          <div
            key={index}
            className="source-item"
          >
            • {source.filename}
          </div>

        ))}

      </div>

    )}

</div>

              {msg.role === "user" && (
                <div className="avatar user">
                  👤
                </div>
              )}

            </div>

          ))}

          {isTyping && (

            <div className="message-row bot">

              <div className="avatar">
                ✦
              </div>

              <div className="message bot typing">

                <span></span>
                <span></span>
                <span></span>

              </div>

            </div>

          )}

          <div ref={chatEndRef}></div>

        </div>

        {/* INPUT */}
        <div className="chat-input">

          <input
            disabled={loading}
            value={query}
            onChange={(e) =>
              setQuery(e.target.value)
            }

            placeholder="Ask something from your uploaded documents..."

            onKeyDown={(e) => {

              if (e.key === "Enter") {

                handleChat();

              }

            }}
          />

          <button
             onClick={handleChat}
             disabled={loading}
>
            ➤
          </button>

        </div>

      

    </div>

    </div>

  );

}

export default App;