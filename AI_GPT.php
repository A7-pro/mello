<?php
ob_start();
error_reporting(0);
define("API_KEY", "7623934999:AAHWkVRZm0-ph6XYfYWFViPxso4WVmKQ8vM"); // Assuming a placeholder key or the user's key. Use the actual key.
$developer_username = '@rnp_e'; // Defined based on luxbox system message
$channel_username = '@mwote'; // Defined based on inline keyboard link

$botname = bot('getme',['bot'])->result->username;
function bot($method, $datas=[]){
$url = "https://api.telegram.org/bot".API_KEY."/$method";
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $datas);
$res = curl_exec($ch);
if(curl_error($ch)){
var_dump(curl_error($ch));
}else{
return json_decode($res);
}
}

$update = json_decode(file_get_contents('php://input'));
$message = $update->message;
$text = $message->text;
$chat_id = $message->chat->id;
$name = $message->from->first_name;
$user = $message->from->username;
$message_id = $update->message->message_id;
$from_id = $update->message->from->id;

function luxbox($message, $developer_username) { // Added developer_username parameter
$url = "https://luxbox.vercel.app/api/chat";
$headers = [
"Content-Type: application/json"
];
$data = [
"message" => $message,
"chatHistory" => [[
"role" => "system",
"content" => "انت ذكاء اصطناعي سعودي , مطور من قبل " . $developer_username . " , موقعك الرسمي هو mikegpt.org , يمكنك الاجابة عن جميع الاسئلة" // Used parameter
],
[
"role" => "user",
"content" => $message
]]];
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
$httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);
if ($httpcode == 200) {
$response_json = json_decode($response, true);
return $response_json['response'] ?? 'عذراً، حدثت مشكلة في الحصول على الإجابة.'; // Modified error message
} else {
return "عذراً، حدثت مشكلة في التواصل مع الخدمة. (HTTP Code: " . $httpcode . ")"; // Added HTTP code for debugging
}
}

if ($text === '/start') {
bot('sendMessage', [
'chat_id' => $chat_id,
'text' => "✨ مرحباً بك يا عزيزي: [" . $name . "](tg://user?id=" . $from_id . ")!\nأنا ذكاء اصطناعي سعودي، مطور بواسطة " . $developer_username . ".\n\nأرسل لي أي سؤال وسأجيبك عليه.", // Reverted to original welcome message structure but kept content
'parse_mode' => 'Markdown',
'reply_to_message_id' => $message_id,
'disable_web_page_preview' => true,
'reply_markup' => json_encode([
'inline_keyboard' => [
[['text' => 'مطور البوت', 'url' => 'https://t.me/rnp_e'], ['text' => 'قناة البوت', 'url' => 'https://t.me/mwote']]
]
])
]);
} else {
$response = luxbox($text, $developer_username); // Passed developer_username
bot('sendMessage', [
'chat_id' => $chat_id,
'text' => $response,
'reply_to_message_id' => $message_id
]);
}
?>
