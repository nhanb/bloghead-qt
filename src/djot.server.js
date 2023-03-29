// TODO: no hardcoded file paths plz
let djot = require("./vendored/djot/djot.js");

let header = [];
let body = [];

process.stdin.on("data", (buffer) => {
  // TODO: loop to read input data in chunks
  let inputSize = buffer.readInt32LE();
  let input = buffer.toString("utf8", 4, 4 + inputSize);
  let output = djot.renderHTML(djot.parse(input));
  let outputBytes = new TextEncoder().encode(output);

  // make a Buffer to utilize writeInt32LE():
  let outputHeaderBuf = Buffer.alloc(4);
  outputHeaderBuf.writeInt32LE(outputBytes.length);

  process.stdout.write(outputHeaderBuf);
  process.stdout.write(outputBytes);
});
