import { useState, useEffect, useRef} from "react";
import { Input, Button, Card, Grid, Text, Divider} from "@geist-ui/core";
import './Style.css'
import { chatLogin, createWebSocket } from './Networking.jsx'

function LoginScreen(
  { username, 
    password, 
    setUsername, 
    setPassword, 
    requestLogin,
    setCreateAccount,
    processing,
    errorMessage
  }) 
{
  return ( 
    <Card shadow style={{margin: "auto", paddingRight: 32, width: "100%", maxWidth: "500px"}}>
      <Grid.Container direction="column" gap={2} justify="center" >
          <Text h1 b>VG CHAT</Text>
          <Divider />

          <Grid style={{ paddingLeft: 34 }}>
            {/* username */}
            <Input 
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </Grid>
          <Grid style={{ paddingLeft: 34 }}>
            {/* password */}
            <Input.Password
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            
            />
          </Grid>

          {/* status code */}
          {errorMessage && (
            <Text type="error" small>{errorMessage}</Text>
          )}
          <Grid>
            {/* Le Button */}
            <Grid.Container justify="center" gap={0.5}>
              <Grid>
                <Button 
                  type="success-light" 
                  onClick={requestLogin}
                  loading={processing}
                  disabled={processing}
                  style={{width: "100%"}}
                >
                  {processing ? "Processing..." : "Login"}
                </Button>
              </Grid>
              <Grid>
                <Button ghost
                  type="success-light" 
                  onClick={() => {setCreateAccount(true);}}
                >
                  Create Account
                </Button>
              </Grid>
            </Grid.Container>
          </Grid>
        </Grid.Container>
    </Card> 
  )
}

function CreateAccountScreen(
  { 
    email,
    username, 
    password, 
    setUsername, 
    setPassword,
    setEmail, 
    requestCreation, 
    setCreateAccount,
    processing,
    errorMessage
  }) 
{
  return ( 
    <Card shadow style={{margin: "auto", paddingRight: 32, width: "100%", maxWidth: "500px"}}>
      <Grid.Container direction="column" gap={2} justify="center" >
          <Text h1 b>VG CHAT</Text>
          <Divider />
          
          <Text>Accounts must follow these criteria:</Text>
          <Grid style={{ paddingRight: 100, paddingLeft: 80 }}>
            <Text small> 
            <ul>
              <li><strong>Username must be equal or longer than 2 characters</strong></li>
              <li><strong>Password must include 1 letter, 1 number, and be 8 or more characters. </strong></li>
              <li><strong>Email must be of valid structure</strong></li>
            </ul>
           </Text>
          </Grid>
          <Grid style={{ paddingLeft: 34 }}>
            {/* username */}
            <Input 
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </Grid>
          <Grid style={{ paddingLeft: 34 }}>
            {/* username */}
            <Input 
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </Grid>
          <Grid style={{ paddingLeft: 34 }}>
            {/* password */}
            <Input.Password
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            
            />
          </Grid>

          {/* status code */}
          {errorMessage && (
            <Text type="error" small>{errorMessage}</Text>
          )}
          <Grid>
            {/* Le Button */}
            <Grid.Container justify="center" gap={0.5}>
              <Grid>
                <Button 
                  type="success-light" 
                  onClick={requestCreation}
                  loading={processing}
                  disabled={processing}
                >
                  {processing ? "Processing..." : "Create Account"}
                </Button>
              </Grid>
              <Grid>
                <Button ghost
                  type="error-light" 
                  onClick={() => {setCreateAccount(false);}}
                >
                  Back
                </Button>
              </Grid>
            </Grid.Container>
          </Grid>
        </Grid.Container>
    </Card> 
  )
}

function ChatWindow(
  {
    messages,
    channels,
    currentChannelId,
    input,
    setInput,
    sendMessageEvent,
    processing,
    sendChannelSwitch,
    activeChannelName
  }
)
{  
  const containerRef = useRef(null);
  const [isMessageContainerAtBottom, setContainerAtBottom] = useState(true);

    // UI events
  const handleScroll = () => {
    const element = containerRef.current;
    if (!element) return;

    const scrollThreshold = 300;
    const isAtBottom = element.scrollHeight - element.scrollTop - element.clientHeight < scrollThreshold;
    
    setContainerAtBottom(isAtBottom);
  }

  
  useEffect(() => {
    const element = containerRef.current;
    if (!element) return;
    
    if (isMessageContainerAtBottom) {
      element.scrollTo({top: element.scrollHeight, behavior: "smooth"});
    }
  }, [messages])

  return (
    <Grid.Container direction="row" justify="center" gap={1}>
      <Grid>
        <Card shadow style={{ height: "100%", maxHeight: "780px" , paddingRight: 30 }}>
          <Text b>Channels</Text>
          <Divider />
            {channels.map((channel) => (
              <Grid key={channel.id}>
                <Button ghost
                  onClick={() => sendChannelSwitch(channel.id)}
                  type={currentChannelId === channel.id ? "success" : "default"}
                >
                  #{channel.name}
                </Button>
              </Grid>
            ))}
        </Card>
      </Grid>
      <Grid>
        <Card shadow style={{paddingRight: 32}}>
          <Text b>#{activeChannelName}</Text>
          <Divider />
          <div ref={containerRef} onScroll={handleScroll} style={{height: 600, minWidth: 600, overflowY: "auto", overflowX:"clip", border: "1px", marginBottom: 12, position: "relative"}}>
              <Grid.Container direction="column" gap={2} justify="center" style={{minWidth: 600, maxWidth: 600}}>
                {messages.map((msg) => (
                  <Grid key={msg.id}>
                    <div style={{textAlign: "left"}}>
                      <div style={{ display: "flex", gap: 8}}>
                          <Text scale={1.05} b>{msg.sender_name}</Text>
                          <Text type="secondary" small>{msg.sent_at}</Text>
                      </div>
                      <Divider />
                      <Text p>{msg.content}</Text>
                    </div>
                  </Grid>
                ))}
              </Grid.Container>
          </div>

          <Input
            placeholder="Type your message here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            width="100%"
          />
          <Button 
            type="success" 
            onClick={sendMessageEvent}
            loading={processing}
            disabled={processing}
          >
          {processing ? "..." : "Send"}
          </Button>
        </Card>
      </Grid>
    </Grid.Container>
  )
}

function App() { 
  // store application state here
  // we implement functions in here cause this is where all of our state is stored
  // each UI component is broken off into two functions for readability

  // login and authentication
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [authToken, setAuthToken] = useState(null);
  const [authErrorMsg, setAuthError] = useState(null);
  const [loginAttemptProcessing, setLoginProcessing] = useState(false);
  const [createAccountProcessing, setCreationProcessing] = useState(false);
  const messageContainerRef = useRef(null);

  // chat state
  const socket = useRef(null);
  const [messages, setMessages] = useState([]); // TODO: refactor to use all redis channels, for now just route to "general"
  const [channels, setChannels] = useState([]);
  const [input, setInput] = useState("");
  const [messageProcesing, setMessageProcessing] = useState(false);
  const [currentChannelId, setCurrentChannel] = useState(1);
  const [activeChannelName, setActiveChannelName] = useState("");
  const [currentUserId, setUserId] = useState(0);

  // UI state
  const [showCreateAccount, setCreateAccount] = useState(false);
  const channelIdRef = useRef(currentChannelId);

  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const passwordPattern = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
  
  const handleCreateAccount = async () => {
    // check lengths
    if (username.length < 2) { setAuthError("Username too short"); return; }
    if (email.length === 0) { setAuthError("Email is empty"); return; }

    if (!passwordPattern.test(password))
    {
      setAuthError("Please make sure password fulfills all requirements");
      return;
    }

    if (!emailPattern.test(email))
    {
        setAuthError("Email is invalid");
        return;
    }

    setCreationProcessing(true);
    setAuthError(null);

    const result = await fetch("/api/users/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "username": username, "password": password, "email": email
        })
    });

    const data = result.json();
    
    if (!result.ok)
    {
      setAuthError(data.detail || "Unexpected error occurred");
      return;
    }

    // after creation log user in
    await handleLoginAttempt();

    setEmail("");
    setUsername("");
    setPassword("");
    setCreateAccount(false);
    setCreationProcessing(false);
  }

  const handleLoginAttempt = async () => {
    setLoginProcessing(true);
    setAuthError(null);

    const result = await chatLogin(username, password);

    try
    {
      if (result.status === "Success") { // auth values provided were valid
        setAuthToken(result.token);
        setUserId(result.user_id);
      }
      else 
      {
        setAuthError(result.status);
      }
    } catch (error) {
      setAuthError("Unresolved network error");
    }
    setCurrentChannel(1);
    setLoginProcessing(false);
  };

  useEffect(() => {
    channelIdRef.current = currentChannelId;
  }, [currentChannelId])

  useEffect(() => {
    if (!authToken) return;

    const sock = createWebSocket(authToken, currentChannelId);

    // events
    sock.onmessage = (e) => { // TODO: add sender username above message
      const message = JSON.parse(e.data);
        if (message.type === "history")
        {
          setMessages(message.messages.map((m) => ({
            id: m._id,
            channel_id: m.channel_id,
            sender_id: m.sender_id,
            sender_name: m.sender_name,
            sent_at: m.sent_at,
            content: m.content
          })));
        }
        else if (message.type === "update_channels")
        {
          setChannels(message.channels.map((m) => ({
            id: m.id,
            name: m.name
          })));
          }
        else if (message.type === "publish")
        {
          if (channelIdRef.current == message.channel_id) 
          {
            setMessages((prev) => [
              ...prev,
              {
                id: message._id || crypto.randomUUID(),
                channel_id: message.channel_id,
                sender_id: message.sender_id,
                sender_name: message.sender_name,
                content: message.content,
                sent_at: message.sent_at
              }
            ])
          }
          else if (message.type === "error")
          {
            setAuthError(message.error_msg);
            console.log(message.error_msg);
          }
      };
    }
    sock.onerror = () => {
      console.log("A socket error occured");
    }

    sock.onclose = () => {
      setAuthError("Connection unexpectedly closed")
      setAuthToken(null);
    }

    socket.current = sock;

    return () => sock.close();
  }, [authToken]);

  const handleMessageSend = () => {
    if (input == "") return;
    
    const sock = socket.current;

    if (!sock || sock.readyState !== WebSocket.OPEN) {
      console.error("Socket not ready");
      return;
    }

    setMessageProcessing(true);
    sock.send(
      JSON.stringify(
        { 
          type: "post", 
          channel: currentChannelId, 
          content: input 
        }
      )
    );

    setInput("");
    setMessageProcessing(false);
  };

  const handleChannelSwitch = (channel_id) => {
    if (channel_id === currentChannelId) return;
    const sock = socket.current;

    if (!sock || sock.readyState !== WebSocket.OPEN) {
      console.error("Socket not ready");
      return;
    }
    setCurrentChannel(channel_id);
    setActiveChannelName(channels.find(c => c.id === channel_id).name);
    setMessages([]);

    sock.send(
      JSON.stringify(
        {
          type: "history",
          channel: channel_id
        }
      )
    )
  }

  return (
    <div
      style={{
        padding: 24,
        maxWidth: 1500,
        margin: "auto",
        width: "100%",
        boxSizing: "border-box"
      }}>
      <div className="app-background" />
      <div className="app-blur" />

      <div className="app-content-display">
        {!authToken ? (
          !showCreateAccount ? (
            <LoginScreen 
              username={username}
              password={password}
              setUsername={setUsername}
              setPassword={setPassword}
              requestLogin={handleLoginAttempt}
              setCreateAccount={setCreateAccount}
              processing={loginAttemptProcessing}
              errorMessage={authErrorMsg}
            />
          ) : (
            <CreateAccountScreen
              username={username}
              password={password}
              email={email}
              setUsername={setUsername}
              setPassword={setPassword}
              setEmail={setEmail}
              requestCreation={handleCreateAccount}
              setCreateAccount={setCreateAccount}
              processing={createAccountProcessing}
              errorMessage={authErrorMsg}
            />
          )
        ) : (
          <ChatWindow 
            messages={messages}
            channels={channels}
            currentChannelId={currentChannelId}
            input={input}
            setInput={setInput}
            sendMessageEvent={handleMessageSend}
            processing={messageProcesing}
            sendChannelSwitch={handleChannelSwitch}
            activeChannelName={activeChannelName}
          />
        )}
      </div>
    </div>
  );
}

export default App;