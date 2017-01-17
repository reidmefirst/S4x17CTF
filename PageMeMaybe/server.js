var http = require('http');
var fs = require('fs');
var formidable = require("formidable");
var util = require('util');

var server = http.createServer(function (req, res) {
    if (req.method.toLowerCase() == 'get') {
        displayForm(res);
    } else if (req.method.toLowerCase() == 'post') {
        processAllFieldsOfTheForm(req, res);
    }

});

function dec2hex(i) {
   return (i+0x10000).toString(16).substr(-4).toUpperCase();
}

function char2hex(c) {
   return (c+0x100).toString(16).substr(-2).toUpperCase();
}

function str2bytearray(s){
   values = []
   for(i = 0; i < s.length; i++){
     values.push(s.charCodeAt(i));
   }
   return values;
}

function int2bytearray(i){
   values = []
   t = i & 0xffff;
   values.push(t >> 8);
   values.push(t & 0xff);
   return values;
}

function string2hex(s) {
  hexout = '';
  l = s.length;
  for (i = 0; i < l; i++){
    hexout += char2hex(s.charCodeAt(i));
  }
  return hexout;
}

function displayForm(res) {
    fs.readFile('form.html', function (err, data) {
        res.writeHead(200, {
            'Content-Type': 'text/html',
                'Content-Length': data.length
        });
        res.write(data);
        res.end();
    });
}


function xorEncrypt(res, data, key, debug) {
    if (debug === undefined){
        debug = "False";
    }
    hexout = '';
    for (i = 0; i < data.length; i++){
      for (j = 0; j < key.length; j++){
        if (debug === "True"){
           res.write('xoring ');
           res.write(data[i]); 
           res.write(' with ');
           res.write( String.fromCharCode(key[j]) );
           res.write( '\n\n');
        }
        hexout += char2hex(data.charCodeAt(i) ^ key[j]);
        i++;
        if(i >= data.length){
          break; // this will break both loops
        }
	if(j+1 >= key.length){
          i--;
        }
      }
    }
    return hexout;
}
function processAllFieldsOfTheForm(req, res) {
    var form = new formidable.IncomingForm();

    form.parse(req, function (err, fields, files) {
	if (!(fields['key'] == 18993 || fields['key'] == 18994)){
		res.writeHead(500, {
			'content-type': 'text/plain' });
		res.writeHead("ILLEGAL PAGING CAPCODE");
		return;
	}
        //Store the data from the fields in your data store.
        //The data store could be a file or database or any other store based
        //on your application.
        res.writeHead(200, {
            'content-type': 'text/plain'
        });
        var encryptedMessage = xorEncrypt(res, fields['message'], int2bytearray(parseInt((fields['key']))));
        execString = "python pocsagtx_pagememaybe.py -m " + encryptedMessage + " -c " + fields['key'];
	// temp KRW

        if(fields['Debug'] === "True"){
       		res.write('received the data:\n\n');
        	res.write(util.inspect({
            		fields: fields,
            		files: files
        	}));
        	res.write('encryption key:\n\n');
        	res.write(fields['key']);
        	res.write('\n\n');
        	res.write("message:\n\n");
        	res.write(fields['message']);
        	res.write('\n\n');
		res.write("Sending to pager: ");
        	res.write(xorEncrypt(res, fields['message'], int2bytearray(parseInt((fields['key'])))));
		res.end('\n\nCalling the pager generator\n\n');
	}
        res.write("Sending page...\n\n");
	//res.write(execString);
	var exec = require('child_process').exec;
	exec(execString, function(error, stdout, stderr){
	        if(fields['Debug'] === "True"){
 			res.write(stdout);
		}
		var sleep = require('sleep');
		sleep.sleep(5);
		res.end("Success, page sent!\n\n");
	});
    	});
}

server.listen(1185);
console.log("server listening on 1185");
