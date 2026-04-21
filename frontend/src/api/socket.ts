import { io } from "socket.io-client";

const socket = io({ transports: ["websocket", "polling"] });

export default socket;
