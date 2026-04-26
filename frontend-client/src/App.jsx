import { useState, useEffect, useRef} from "react";
import { Input, Button, Card, Text, Divider} from "@geist-ui/core";
import './Style.css'
import { chatLogin, createWebSocket} from './Networking.jsx'

function LoginScreen(
  { username, 
    password, 
    setUsername, 
    setPassword, 
    requestLogin, 
    processing,
    errorMessage
  }) 
{
  return ( 
      <Card shadow='true' style={{alignContent: "center"}}>
        <Card.Content>
          <Text h1><b>VG CHAT</b></Text>
        </Card.Content>
        <Divider h="2px" my={0} />
        <Card.Content>
          <Text h3>Login</Text>
          
          {/* username */}
          <Input 
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            
          />
          {/* password */}
          <Input.Password
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          
          />

          {/* status code */}
          {errorMessage && (
            <Text type="error" small>{errorMessage}</Text>
          )}

          {/* Le Button */}
          <Button 
            type="success-light" 
            onClick={requestLogin}
            loading={processing}
            disabled={processing}
          >
            {processing ? "Processing..." : "Login"}
          </Button>
        </Card.Content>
      </Card> 
  )
}

function ChatWindow(
  {
    messages,
    input,
    setInput,
    sendMessageEvent,
    processing
  }
)
{
  return (
    <Card>
      <div style={{height: 250, overflowY: "auto", border: "1px", padding: 10, marginBottom: 12}}>
          {messages.map((msg, i) => (
            <div key={i}>
              <Text>{msg}</Text>
            </div>
          ))}
      </div>

      <Input
        placeholder="Type your message here..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        width="100%"
      />
      <Button 
        type="secondary-light" 
        onClick={sendMessageEvent}
        loading={processing}
        disabled={processing}
      >
      {processing ? "..." : "Send"}
      </Button>
    </Card>
  )
}

function App() { 
  // store application state here
  // we implement functions in here cause this is where all of our state is stored
  // each UI component is broken off into two functions for readability

  // login and authentication
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [authToken, setAuthToken] = useState(null);
  const [authErrorMsg, setAuthError] = useState(null);
  const [loginAttemptProcessing, setLoginProcessing] = useState(false);

  // chat state
  const socket = useRef(null);
  const [messages, setMessages] = useState([]); // TODO: refactor to use all redis channels, for now just route to "general"
  const [input, setInput] = useState("");
  const [messageProcesing, setMessageProcessing] = useState(false);

  const handleLoginAttempt = async () => {
    setLoginProcessing(true);
    setAuthError(null);

    const result = await chatLogin(username, password);

    try
    {
      if (result.status === "Success") { // auth values provided were valid
        setAuthToken(result.token);
      }
      else 
      {
        setAuthError(result.status);
      }
    } catch (error) {
      setAuthError("Unresolved network error");
    }

    setLoginProcessing(false);
  };

  useEffect(() => {
    if (!authToken) return;

    const sock = createWebSocket(authToken);

    // events
    sock.onmessage = (e) => { // TODO: add sender username above message
      setMessages((prev) => [...prev, e.data]);
    };

    socket.current = sock;

    return () => sock.close();
  }, [authToken]);

  const handleMessageSend = () => {
    const sock = socket.current;

    if (!sock || sock.readyState !== WebSocket.OPEN) {
      console.error("Socket not ready");
      return;
    }

    setMessageProcessing(true);

    sock.send(
      JSON.stringify({ channel: "general", content: input })
    );

    setInput("");
    setMessageProcessing(false);
  };

  return (
    <div 
      style={{
        padding: 24,
        maxWidth: 600,
        margin: "auto",
        width: "100%",
        boxSizing: "border-box"
      }}
    >
      {!authToken ? (
        <LoginScreen 
          username={username}
          password={password}
          setUsername={setUsername}
          setPassword={setPassword}
          requestLogin={handleLoginAttempt}
          processing={loginAttemptProcessing}
          errorMessage={authErrorMsg}
        />
      ) : (
        <ChatWindow 
          messages={messages}
          input={input}
          setInput={setInput}
          sendMessageEvent={handleMessageSend}
          processing={messageProcesing}
        />
      )}
    </div>
  );
}

export default App;