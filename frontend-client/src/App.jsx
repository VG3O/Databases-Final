import { useState, useEffect } from "react";
import './Style.css'




function CreateUser() {
  const [username, setUsername] = useState(""); 
  const [email, setEmail] = useState("");
  const [processing, setProcessing] = useState(false);
  

  const handleClick = async (event) => {
    event.preventDefault();
    setProcessing(true);

    let url = "/api/users/"

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({"username": username, "email": email})
      });
      if (!response.ok) {
        throw new Error('Response status: ${response.status}');
      }

      setProcessing(false);
    } catch (err) {
      console.error(err.message);
      setProcessing(false);
    }
    
    setEmail("")
    setUsername("")
  }

  return (
    <div>
      <input 
        type="text"
        placeholder="username"
        value={username}
        onChange={(event) => setUsername(event.target.value)}
      />
      <input 
        type="text"
        placeholder="email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
      />
      <button onClick={handleClick} disabled={processing}>Create User</button>
    </div>
  )
}

function UsersTable() {
  const [users, setUsers] = useState([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [activeUsers, setActiveUsers] = useState(0);

  async function fetchUsers() {
    const response = await fetch("/api/users/");
    const responseData = await response.json();
    
    setUsers(responseData.userData);
    setTotalUsers(responseData.totalRegistered);
    setActiveUsers(responseData.activeUsers);
  }

  useEffect(() => {
    fetchUsers();

    const userTableInterval = setInterval(async () => {
      await fetchUsers();
    }, 5000)

    return () => clearInterval(userTableInterval);
  }, []);

  return (
    <table border="2" align="center">
      <caption class="tableheader">Registered Users: {totalUsers}</caption>
      <thead>
        <th>user_id</th>
        <th>username</th>
        <th>email</th>
        <th>creation_date</th>
      </thead>

      <tbody>
        {
          users.map(user => (
            <tr key={user.id}>
              <td class="userid">{user.id}</td>
              <td>{user.user_name}</td>
              <td>{user.email}</td>
              <td>{user.created_at}</td>
            </tr>
          ))
        }
      </tbody>
    </table>
  )
}

function MessageLog() {
  const [messages, setMessages] = useState([]);

  async function fetchMessages() {
    const response = await fetch("/api/messages/");
    const responseData = await response.json();
    console.log(responseData.messages);
    setMessages(responseData.messages);
  }

  useEffect(() => {
    fetchMessages();

    const messageLogInterval = setInterval(async () => {
      await fetchMessages();
    }, 5000)

    return () => clearInterval(messageLogInterval);
  }, []);

  return (
    <table border="2" align="center">
      <caption class="tableheader">Message Log</caption>
      <thead>
        <th>sender_id</th>
        <th>content</th>
        <th>sent_timestamp</th>
      </thead>

      <tbody>
        {
          messages.map(msg => (
            <tr key={msg.sent_at}>
              <td class="userid">{msg.sender_id}</td>
              <td>{msg.content}</td>
              <td>{msg.sent_at}</td>
            </tr>
          ))
        }
      </tbody>
    </table>
  )
}

function SendMessage() {
  const [messageContent, setContent] = useState(""); 
  const [processing, setProcessing] = useState(false);
  
  const handleClick = async (event) => {
    event.preventDefault();
    setProcessing(true);

    let url = "/api/messages/"

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({"content": messageContent, "sender_id": 1})
      });
      if (!response.ok) {
        throw new Error('Response status: ${response.status}');
      }

      setProcessing(false);
    } catch (err) {
      console.error(err.message);
      setProcessing(false);
    }
    
    setContent("")
  }

  return (
    <div>
      <input 
        type="text"
        placeholder="Type to send a message..."
        value={messageContent}
        onChange={(event) => setContent(event.target.value)}
      />
      <button onClick={handleClick} disabled={processing}>Send Message</button>
    </div>
  )
}

function App() { 

  return (
    <div class="content_display">
      <h1>Testing Dashboard</h1>
      <CreateUser />
      <br />
      <UsersTable />
      <br />
      <MessageLog />
      <SendMessage />
    </div>
  );
}


export default App;