import React, { useState, useRef, useEffect } from "react";

// --- Icons (SVG) for Theme Toggle ---
const MoonIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
  </svg>
);

const SunIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="5"></circle>
    <line x1="12" y1="1" x2="12" y2="3"></line>
    <line x1="12" y1="21" x2="12" y2="23"></line>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
    <line x1="1" y1="12" x2="3" y2="12"></line>
    <line x1="21" y1="12" x2="23" y2="12"></line>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
  </svg>
);

function App() {
  const [theme, setTheme] = useState("dark");
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Chào bạn! Bạn muốn tôi vẽ mô hình 3D nào hôm nay?",
    },
    {
      sender: "bot",
      text: 'Hãy thử các prompt như: "vẽ một quả cầu", "tạo hình bánh donut", "vẽ một mặt phẳng hình sin" ',
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { sender: "user", text: inputValue };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/generate-plot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: inputValue }),
      });

      const data = await response.json();

      if (response.ok && data.html) {
        // SỬA LỖI: Thêm CSS để ghi đè chiều cao cố định của Plotly
        const fullHtml = `
                  <html>
                    <head>
                      <meta name="viewport" content="width=device-width, initial-scale=1" />
                      <style>
                        /* Allow the plot to size to the iframe and allow internal scroll if plot is taller */
                        html, body {
                          margin: 0;
                          padding: 0;
                          width: 100%;
                          height: 100%;
                          box-sizing: border-box;
                        }
                        /* Make common Plotly containers fill available space */
                        .plotly, .js-plotly-plot, .main-svg, .svg-container, .plot-container {
                          width: 100% !important;
                          height: 100% !important;
                          min-height: 100% !important;
                        }
                        /* Allow the iframe to add its own scrollbar if necessary */
                        body > div { box-sizing: border-box; }
                      </style>
                    </head>
                    <body>
                      ${data.html}
                    </body>
                  </html>
                `;
        const botMessage = { sender: "plot", html: fullHtml };
        setMessages((prev) => [...prev, botMessage]);
      } else {
        const errorMessage = {
          sender: "bot",
          text: `Rất tiếc, đã có lỗi: ${
            data.detail || "Không thể xử lý yêu cầu."
          }`,
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error("Lỗi khi gọi API:", error);
      const errorMessage = {
        sender: "bot",
        text: "Không thể kết nối tới server. Vui lòng kiểm tra lại.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <style>
        {`
            :root {
              --light-bg: #f5f5f5;
              --light-text: #1a1a1a;
              --light-header-bg: #ffffff;
              --light-border: #ddd;
              --light-bot-message-bg: #e9e9eb;
              --light-input-bg: #f0f0f0;

              --dark-bg: #1a1a1a;
              --dark-text: #f5f5f5;
              --dark-header-bg: #242424;
              --dark-border: #333;
              --dark-bot-message-bg: #333;
              --dark-input-bg: #333;

              --primary-color: #007bff;
            }

            body {
              margin: 0;
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
            }

            .app-container {
              display: flex;
              flex-direction: column;
              height: 100vh;
              transition: background-color 0.3s, color 0.3s;
              overflow: hidden;
            }

            .app-container.light {
              background-color: var(--light-bg);
              color: var(--light-text);
            }

            .app-container.dark {
              background-color: var(--dark-bg);
              color: var(--dark-text);
            }
            
            .header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              padding: 1rem;
              border-bottom: 1px solid;
              transition: background-color 0.3s, border-bottom 0.3s;
              flex-shrink: 0;
            }

            .app-container.light .header {
              background-color: var(--light-header-bg);
              border-bottom-color: var(--light-border);
            }
            .app-container.dark .header {
              background-color: var(--dark-header-bg);
              border-bottom-color: var(--dark-border);
            }

            .title { margin: 0; font-size: 1.5rem; }
            .theme-toggle-button { background: none; border: none; cursor: pointer; }
            .app-container.light .theme-toggle-button { color: var(--light-text); }
            .app-container.dark .theme-toggle-button { color: var(--dark-text); }

            /* SỬA LỖI CUỘN */
            .messages-container {
              flex: 1 1 0;
              /* allow children to shrink properly inside flex container */
              min-height: 0;
              overflow-y: auto; 
              padding: 1rem;
              display: flex;
              flex-direction: column;
            }

            .message-wrapper {
              display: flex;
              align-items: flex-start;
              margin-bottom: 0.5rem;
              max-width: 75%;
              /* keep message height, don't shrink in flex list */
              flex: 0 0 auto;
            }

            .message-wrapper.user {
              align-self: flex-end;
              flex-direction: row-reverse;
            }

            .message-wrapper.bot {
              align-self: flex-start;
            }

            .bot-avatar {
              width: 40px;
              height: 40px;
              border-radius: 50%;
              margin-right: 0.5rem;
              flex-shrink: 0;
              object-fit: cover;
              border: 2px solid rgba(0, 123, 255, 0.3);
            }

            .message {
              padding: 0.75rem 1rem;
              border-radius: 18px;
              line-height: 1.4;
              animation: slideInFadeIn 0.4s ease-out forwards;
              word-wrap: break-word;
              flex: 1;
            }

            .user-message {
              background-color: var(--primary-color);
              color: white;
            }

            .bot-message {
              transition: background-color 0.3s, color 0.3s;
            }

            .app-container.light .bot-message {
              background-color: var(--light-bot-message-bg);
              color: var(--light-text);
            }
            .app-container.dark .bot-message {
              background-color: var(--dark-bot-message-bg);
              color: var(--dark-text);
            }

            .plot-container {
              align-self: center;
              width: 95%;
              max-width: 1000px;
              /* prefer a flexible height but keep a sensible max */
              height: 600px;
              max-height: 80vh;
              background-color: #fff;
              border-radius: 12px;
              margin: 1rem 0;
              box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
              overflow: hidden;
              animation: slideInFadeIn 0.4s ease-out forwards;
              /* keep plot from shrinking */
              flex: 0 0 auto;
            }

            .plot-iframe { width: 100%; height: 100%; border: none; display: block; }

            .input-form {
              display: flex;
              padding: 1rem;
              border-top: 1px solid;
              transition: background-color 0.3s, border-top 0.3s;
              flex-shrink: 0; 
            }
            .app-container.light .input-form {
              background-color: var(--light-header-bg);
              border-top-color: var(--light-border);
            }
            .app-container.dark .input-form {
              background-color: var(--dark-header-bg);
              border-top-color: var(--dark-border);
            }

            .input {
              flex: 1;
              padding: 0.75rem;
              border-radius: 20px;
              border: 1px solid;
              font-size: 1rem;
              margin-right: 0.5rem;
              transition: background-color 0.3s, color 0.3s, border 0.3s;
            }
            .app-container.light .input {
              border-color: #ccc;
              background-color: var(--light-input-bg);
              color: var(--light-text);
            }
            .app-container.dark .input {
              border-color: #444;
              background-color: var(--dark-input-bg);
              color: var(--dark-text);
            }
            
            .button {
              padding: 0.75rem 1.5rem;
              border-radius: 20px;
              border: none;
              background-color: var(--primary-color);
              color: white;
              cursor: pointer;
              font-size: 1rem;
            }
            .button:disabled { opacity: 0.6; cursor: not-allowed; }
            
            @keyframes slideInFadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            
            .loading span {
                opacity: 0;
                animation: pulse 1.4s infinite;
            }
            .loading span:nth-child(1) { animation-delay: 0s; }
            .loading span:nth-child(2) { animation-delay: 0.2s; }
            .loading span:nth-child(3) { animation-delay: 0.4s; }

            @keyframes pulse { 0%, 100% { opacity: 0; } 50% { opacity: 1; } }
        `}
      </style>
      <div className={`app-container ${theme}`}>
        <header className="header">
          <h1 className="title">Trình tạo mô hình 3D</h1>
          <button
            className="theme-toggle-button"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <SunIcon /> : <MoonIcon />}
          </button>
        </header>
        <div className="messages-container">
          {messages.map((msg, index) => {
            if (msg.sender === "plot") {
              return (
                <div key={index} className="plot-container">
                  <iframe
                    title={`plot-${index}`}
                    srcDoc={msg.html}
                    className="plot-iframe"
                  />
                </div>
              );
            }
            return (
              <div key={index} className={`message-wrapper ${msg.sender}`}>
                {msg.sender === "bot" && (
                  <img
                    src="/img/bot_img.jpg"
                    alt="Bot Avatar"
                    className="bot-avatar"
                  />
                )}
                <div
                  className={`message ${
                    msg.sender === "user" ? "user-message" : "bot-message"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            );
          })}
          {isLoading && (
            <div className="message-wrapper bot">
              <img
                src="/img/bot_img.jpg"
                alt="Bot Avatar"
                className="bot-avatar"
              />
              <div className="message bot-message loading">
                Đang xử lý<span>.</span>
                <span>.</span>
                <span>.</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form className="input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            className="input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Nhập yêu cầu của bạn ở đây..."
            disabled={isLoading}
          />
          <button type="submit" className="button" disabled={isLoading}>
            Gửi
          </button>
        </form>
      </div>
    </>
  );
}

export default App;
