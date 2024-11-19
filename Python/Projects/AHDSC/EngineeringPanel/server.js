keys = []

const sleep = delay => new Promise(resolve => setTimeout(resolve, delay))

function decode (packed_list) {
  var strippedText = String(packed_list)
  strippedText = strippedText.split(/\r?\n/)
  for (let variable of strippedText) {
    var variable2 = variable.split(':')
    strippedText[strippedText.indexOf(variable)] = variable2
  }
  return strippedText
}

function encode (list) {
  var returnval = ''
  for (let sect of list) {
    returnval += String(sect[0]) + ':' + String(sect[1]) + '\n'
  }
  return returnval
}

async function startWebsocket (uri) {
    const socket = new WebSocket(`ws://${uri}`)
    socket.onopen = event => {
      socket.send(encode(keys))
    }
    socket.addEventListener('message', event => {
      console.log('Message from server ', event.data)
      keys = decode(event.data)
    })
}

startWebsocket('localhost:8766')