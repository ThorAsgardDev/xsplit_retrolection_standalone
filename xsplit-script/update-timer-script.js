/*
    This loads text from [FILEPATH] in between [DELIMITER_1] and [DELIMITER_2].
    If [DELIMITER_1] and [DELIMITER_2] is not found, Title shows the whole text.
    An optional [UPDATEINTERVAL] in milliseconds may also be set to auto-update.
    The script will check the local file for any changes in text every [UPDATEINTERVAL] milliseconds
    which will automatically update the text within the stage.
    Setting it to 0 or lower disables auto-update.  
*/

/**
 * @name FILEPATH
 * @label File Path
 * @type file
 * @filters "Text Files (*.txt)|*.txt|All Files (*.*)|*.*||"
 * @description The path of the file from where the script will extract text
 */
var FILEPATH = "d:\\sample path\\sample.txt";

/**
 * @name DELIMETER_1
 * @label Delimeter 1
 * @type text
 * @description The text, which when found signals the start of extracting text. If not found, script will show the whole text.
 */
var DELIMETER_1 = "<html>";

/**
 * @name DELIMETER_2
 * @label Delimeter 2
 * @type text
 * @description The text, which when found signals the end of extracting text. If not found, script will show the whole text.
 */
var DELIMETER_2 = "</html>";

/**
 * @name UPDATEINTERVAL
 * @label Update Interval
 * @type int
 * @positiveOnly true
 * @description Optional. If set, the script will check the local file for any changes in text every X seconds, which will automatically update the text within the stage.
 */
var UPDATEINTERVAL = 1;

/**
 * @name LINEBREAK_BEHAVIOR
 * @label Behavior on Line Breaks
 * @type select
 * @options Preserve Line Breaks||Ignore Line Breaks||Replace
 * @description Preserve Line Breaks = Line breaks will be preserved, and text will be wrapped to the next line||Ignore Line Breaks = Line breaks will simply be omitted, and without spacing. Text will be displayed on single line||Replace = Replace line breaks with a specific character or set of characters
 */
var LINEBREAK_BEHAVIOR = "Replace";

/**
 * @name REPLACE_WITH
 * @label Replace Line Break With
 * @type text
 * @description The text to replace line breaks with, if Replace is selected as line break behavior
 */
var REPLACE_WITH = " ";

/*Do not modify anything below*/

/**
 * @name XJS_URL
 * @description XJS FRAMEWORK URL LOCATION
*/
var XJS_URL = "http://cdn2.xsplit.com/xjs/download/1.4.1/xjs.min.js?source"; 

function loadScript(url, callback)
{
    // Adding the script tag to the head
    var head = document.getElementsByTagName('head')[0];
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;    

    // Then bind the event to the callback function.
    // There are several events for cross browser compatibility.
    script.onreadystatechange = callback;
    script.onload = callback;

    // Fire the loading
    head.appendChild(script);
}

var XJS;

var oldResponse;

function processText(response)
{    
    
    var responseCleaned;

    if (LINEBREAK_BEHAVIOR == "Ignore Line Breaks")
    {
        responseCleaned = response.replace(/(\r\n|\n|\r)/gm,"");
    }
    else if (LINEBREAK_BEHAVIOR == "Replace")
    {
        responseCleaned = response.replace(/(\r\n|\n|\r)/gm, REPLACE_WITH);
    }
    else
    {
        responseCleaned = response.replace(/(\r\n|\n|\r)/gm,"<br>");
    }

    if (DELIMETER_1 != "" && DELIMETER_2 != "")
    {
        var responseCleanedLength = responseCleaned.length;
        var indexOfDelim1 = responseCleaned.indexOf(DELIMETER_1) > -1 ? (responseCleaned.indexOf(DELIMETER_1) + DELIMETER_1.length) : 0;
        var substringResponseCleaned = responseCleaned.substring(indexOfDelim1);
        var substringResponseCleanedLength = substringResponseCleaned.length;

        var initialIndexOfDelim2 = substringResponseCleaned.indexOf(DELIMETER_2) > -1 ? substringResponseCleaned.indexOf(DELIMETER_2) : responseCleanedLength;
        var indexOfDelim2 = responseCleanedLength;
        if (initialIndexOfDelim2 != responseCleanedLength)
        {
            indexOfDelim2 = initialIndexOfDelim2 + (responseCleanedLength - substringResponseCleanedLength);
        }

        if (indexOfDelim2 <= indexOfDelim1)
            indexOfDelim2 = responseCleaned.length - 1;
        responseCleaned = responseCleaned.substring(indexOfDelim1, indexOfDelim2);
    }
    
    if(oldResponse!=responseCleaned)
    {
        SetText(responseCleaned, "Local File: " + FILEPATH);
    }
    oldResponse=responseCleaned;
    if (UPDATEINTERVAL > 0)
    {
        smlTitleTimeouts = setTimeout(function() { GetTextFromRemote(0); }, UPDATEINTERVAL*1000);
    }     

}

function GetTextFromRemote(nRetries){
    var response;

    XJS.IO.getFileContent(FILEPATH).then(function(base64Content) {
        try {
            response = decodeURIComponent(escape(window.atob(base64Content)));
            if(response == "" && nRetries < 5) {
                smlTitleTimeouts = setTimeout(function(nRetries) { GetTextFromRemote(nRetries); }, 10, nRetries + 1);
            } else {
                processText(response);
            }
        } catch(err) {
            return new Promise(function(resolve, reject) {
                reject("ERROR: " + err.stack);
          });
        }        
    }).catch(function(err) {
        XJS.IO.getFileContent(FILEPATH).then(function(base64Content) {
            response = window.atob(base64Content);
            processText(response); 
        });
    });                      
     
}

if (smlTitleTimeouts && smlTitleTimeouts != null)
    {clearTimeout(smlTitleTimeouts);}

SetText("", "Local File: " + FILEPATH);

var loadScriptCallback = function() {           
    XJS = require('xjs');
    XJS.ready()
    .then(function() { 
        GetTextFromRemote(0)
    })
};


loadScript(XJS_URL, loadScriptCallback);    