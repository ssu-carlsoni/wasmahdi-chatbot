var initialMessage = "";
var chatbot_dp = "";
var chatbot_name = '';
var chatbot_toggle_picture = "";
var user_chatmessage_color = "";
var bot_chatmessage_color = "";
const backend_url = "https://backend-wgh5.vercel.app"

fetch(`${backend_url}/v1/chatbot/settings`, {
  method: 'GET',
  headers: {
    'accept': 'application/json',
    'x-author': '7yr82hwerwehfbwy94rkjbwef975b32497897243hbsbjkdshbqhwoiuqerbhf'
  }
})
  .then(response => response.json())
  .then(data => {
    if(data.success == false){
        return;
    }
    
    initialMessage = data.data.frontend.initial_message;
    chatbot_name = data.data.frontend.chatbot_name;
    chatbot_dp = data.data.frontend.chatbot_dp_url;
    chatbot_toggle_picture = data.data.frontend.widget_button_url;
    user_chatmessage_color = data.data.frontend.user_message_color;
    bot_chatmessage_color = data.data.frontend.chatbot_message_color;

    function createStyles() {
    
        const styles = `
        body {
        margin: 0;
        padding: 0;
        /* Add any other styles for your page here */
        }
    
        /* Style the widget container */
        .widget-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        }
    
        /* Style the widget button */
        .widget-button {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        /* background-color:; */
        background-color: #fff;
        padding: 1; /* Remove default padding */
        border: none;
        cursor: pointer;
        shape-outside: 10px;
        background-image: url(${chatbot_toggle_picture});
        background-size: 100% 100%; /* You can use other values like "100% 100%" or "50% 50%" */
        background-position: center; /* Center the image within the button */
        background-repeat: no-repeat; /* Prevent image repetition */
        }
    
        .widget {
        display: none;
        background-color: #f2f2f2;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 20px;
        background-color:#fff;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        /* Position the chatbot container at the top of the button */
        position: absolute;
        top: -652px; /* Adjust this value to position the widget as desired */
        right: 0;
        height: 500x; /* Increase the height by 20% (300px + 20%) */
        width: 440px; /* Increase the width by 20% (250px + 20%) */
        overflow: hidden;
        /* Add a CSS transition to create a smooth upward movement effect */
        transition: top 0.3s ease;
        scrollbar-width:thin;
        scrollbar-color: #c4d4da #f2f2f2;
        }
        /* Style the chat messages container scroll bar track */
        #chatMessagesContainer::-webkit-scrollbar {
        width: 4px; /* Width of the scroll bar */
        }
    
        /* Style the chat messages container scroll bar thumb */
        #chatMessagesContainer::-webkit-scrollbar-thumb {
        background-color: #c4d4da; /* Color of the scroll bar thumb */
        border-radius: 10px; /* Radius of the scroll bar thumb */
        }
    
        /* Style chat messages container */
        #chatMessagesContainer {
        height: 470px; /* Increase the height by 20% (240px + 20%) */
        overflow-y: auto; /* Enable vertical scrolling for overflow */
        margin-bottom: 18px;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 15px;
        }
    
        #chatMessages {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        }
    
        /* Style user messages */
        #chatMessages .user-message {
        background-color: ${user_chatmessage_color};
        padding: 5px 10px;
        border-radius: 7px;
        display: inline-block;
        max-width: 65%;
        word-wrap: break-word;
        align-self: flex-end;
        margin-bottom: 5px;
        font-size:20px;
        font-family: Garamond, serif;
        }
    
        /* Style bot messages */
        #chatMessages .chatbot-message {
        background-color: ${bot_chatmessage_color};
        color: #fff;
        padding: 5px 10px;
        border-radius: 7px;
        display: inline-block;
        max-width: 65%;
        word-wrap: break-word;
        align-self: flex-start;
        margin-bottom: 5px;
        font-size:20px;
        font-family: Garamond, serif;
        }
    
        /* Style the chat input */
        .chat-input {
        display: flex;
        }
    
        .chat-input input {
        flex: 1;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        }
    
        .chat-input button {
        padding: 5px 10px;
        margin-left: 10px;
        border: none;
        background-color: ${bot_chatmessage_color};
        color: #fff;
        border-radius: 5px;
        cursor: pointer;
        }
        /* Style the chatbot header */
        .chat-header {
        display: flex;
        align-items: center;
        padding-bottom: 10px;
        border-bottom: 1px solid #ccc;
        margin-bottom: 10px;
        }
    
        .chat-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        margin-right: 10px;
        }
    
        .chatbot-name {
        font-weight:bold;
        font-size:25px;
        font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;
        color:grey;
        }
        .typing-dot {
        animation: typing 1s infinite;
        }
    
        @keyframes typing {
        0%, 100% { opacity: 0; }
        50% { opacity: 1; }
        }
    
        `;
    
        const styleElement = document.createElement('style');
        styleElement.appendChild(document.createTextNode(styles));
        document.head.appendChild(styleElement);
    }
    
    function createElement(elementType, attributes = {}, content = "") {
        const element = document.createElement(elementType);
        for (const key in attributes) {
            if (attributes.hasOwnProperty(key)) {
                element.setAttribute(key, attributes[key]);
            }
        }
        
        if (content.startsWith('http') || content.startsWith('data:image')) {
            const image = document.createElement('img');
            image.src = content;
            element.appendChild(image);
        } else {
            element.textContent = content;
        }
        
        return element;
    }
    
    
    createStyles();
    
    
    const widgetContainer = createElement('div', { class: 'widget-container' });
    const chatButton = createElement('button', { id: 'chatButton', class: 'widget-button' });
    const chatbotContainer = createElement('div', { id: 'chatbot', class: 'widget' });
    const chatHeader = createElement('div', { class: 'chat-header' });
    const chatAvatar = createElement('img', { src: chatbot_dp, alt: 'Chatbot Avatar', class: 'chat-avatar' });
    const chatbotName = createElement('span', { class: 'chatbot-name' }, chatbot_name);
    const MessagesContainer = createElement('div', { id: 'chatMessagesContainer' });
    const chatMessages = createElement('ul', { id: 'chatMessages' });
    const chatInput = createElement('div', { class: 'chat-input' });
    const userInput = createElement('input', { type: 'text', id: 'userInput', placeholder: 'Type your message...' });
    const sendButton = createElement('button', { id: 'sendButton' });
    const image = document.createElement('img');
    
    image.src = 'send.png';
    image.style.width = '20px';
    image.style.height = '20px';
    sendButton.style.padding = '10px 10px 5px';
    sendButton.appendChild(image);
    chatHeader.appendChild(chatAvatar);
    chatHeader.appendChild(chatbotName);
    
    chatInput.appendChild(userInput);
    chatInput.appendChild(sendButton);
    
    chatbotContainer.appendChild(chatHeader);
    chatbotContainer.appendChild(MessagesContainer);
    chatbotContainer.appendChild(chatInput);
    
    MessagesContainer.appendChild(chatMessages);
    widgetContainer.appendChild(chatButton);
    widgetContainer.appendChild(chatbotContainer);
    
    document.body.appendChild(widgetContainer);
    
    const chatbot = document.getElementById('chatbot');
    const chatBtn = document.getElementById('chatButton');
    const chatMsgs = document.getElementById('chatMessages');
    const userQuery = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendButton');
    const chatMessagesContainer = document.getElementById('chatMessagesContainer');
    
    let chatbotVisible = false;
  
    function addChatMessageNoTyping(text, isUser) {
        const messageClass = isUser ? 'user-message' : 'chatbot-message';
        const listItem = document.createElement('li');
        listItem.className = messageClass;
        listItem.innerText = text;
        chatMsgs.appendChild(listItem);
    
        
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }
  
    function saveConversationToLocalStorage(conversation) {
        localStorage.setItem('chatbotConversation', JSON.stringify(conversation));
    }
    function isConversationHistoryEmpty() {
        const conversation = loadConversationFromLocalStorage();
        return conversation.length;
    }
    
    
    function loadConversationFromLocalStorage() {
        const conversation = JSON.parse(localStorage.getItem('chatbotConversation'));
        if (conversation && conversation.length > 0) {
            return conversation;
        }
        return [];
    }
    
    
    function loadMessageHistory() {
        const conversation = loadConversationFromLocalStorage();
        conversation.forEach((message) => {
            const { role, content } = message;
            if (role === 'user') {
                addChatMessage(content, true);
            } else {
                addChatMessageNoTyping(content, false);
            }
        });
    }
    function deleteConversationFromLocalStorage() {
        localStorage.removeItem('chatbotConversation');
    }
    
    
    function toggleChatbot() {
    chatbotVisible = !chatbotVisible;
    chatbot.style.display = chatbotVisible ? 'block' : 'none';
    
    if (chatbotVisible) {
        
        chatbot.style.top = '-652px';
        setTimeout(() => {
        
        if(isConversationHistoryEmpty() == 0){
            addChatMessageTyping(initialMessage, false);
            
            };
        }, 500);
        loadMessageHistory();
    } else {
        
        chatbot.style.top = '-652px';
        chatMsgs.innerHTML = '';
        userQuery.value = '';
    }
    }
    
    
    function addChatMessage(text, isUser) {
    const messageClass = isUser ? 'user-message' : 'chatbot-message';
    const listItem = document.createElement('li');
    listItem.className = messageClass;
    listItem.innerText = text;
    chatMsgs.appendChild(listItem);
    
    
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }
    
    function addChatMessageTyping(text, isUser) {
        const messageClass = isUser ? 'user-message' : 'chatbot-message';
        const listItem = document.createElement('li');
        listItem.className = messageClass;
        chatMsgs.appendChild(listItem);
    
    
        function typeText(i) {
        if (i < text.length) {
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
            listItem.innerHTML = text.substring(0, i + 1) + '<span class="typing-dot">.</span>';
            i++;
            setTimeout(() => typeText(i), 8);
        } else {
            listItem.innerHTML = text;
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        }
        }
    
        typeText(0);
    }
    
    
    function openChatbot(timestamp) {
        if (!chatbot.startTime) chatbot.startTime = timestamp;
        const progress = Math.min((timestamp - chatbot.startTime) / 300, 1); // 300ms for animation duration
        chatbot.style.top = `${-340 + 340 * progress}px`; // Slide chatbot down
        if (progress < 1) {
        requestAnimationFrame(openChatbot);
        }
    }
    

    function handleUserInput() {
    const userMessage = userQuery.value;
    userQuery.value = '';
    if (userMessage.trim() !== '') {
        addChatMessage(userMessage, true);
    
        if(isConversationHistoryEmpty() == 0){
            saveConversationToLocalStorage([
            ...loadConversationFromLocalStorage(),
            { role: 'chatbot', content: initialMessage }
        ]);
        }
        saveConversationToLocalStorage([
            ...loadConversationFromLocalStorage(),
            { role: 'user', content: userMessage }
        ]);
        
        
        const apiUrl = `${backend_url}/v1/chatbot/chat`;
        const requestData = {
            query: userMessage
        };
        const requestOptions = {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'x-author': '7yr82hwerwehfbwy94rkjbwef975b32497897243hbsbjkdshbqhwoiuqerbhf'
            },
            body: JSON.stringify(requestData)
        };
    
        fetch(apiUrl, requestOptions)
        .then(response => {
            if (response.ok) {
                return response.json(); 
              } else {
                throw new Error('Failed to fetch data from the API');
              }
        })
        .then(data => {

            var responseText = data.message;
                addChatMessageTyping(responseText.replace(/\n/g, "<br>"), false);
                saveConversationToLocalStorage([
                    ...loadConversationFromLocalStorage(),
                    { role: 'chatbot', content: responseText }
                ]);
                userQuery.value = '';
        })
        .catch(error => {
            console.error(error);
        });
        
    }
    }
    
    chatBtn.addEventListener('click', toggleChatbot);
    

    sendBtn.addEventListener('click', handleUserInput);
    
    userQuery.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        handleUserInput();
    }
    });
  })

.catch(error => {
console.error('Error fetching data:', error);
});
