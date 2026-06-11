var FIXED="";
var CheckMovement="";
var CURclientX = 0;
var CURclientY = 0;
var WPT_GLOB_event="";

var SHADOW_T = 0;
var SHADOW_B = 0;
var SHADOW_L = 0;
var SHADOW_R = 0;
 
    let SL_WPToriginalTextIsShowing = false
    let divElement
    let shadowRoot
    let styleTextContent = ""
    const mousePos = {
        x: 0,
        y: 0
    }


window.addEventListener('mousemove', function (event) {	
	WPT_GLOB_event = event
	if(ACTIVATED==1){		
	    if(CUR_MO != 0){
		var CheckMovement = window.setTimeout(function() {
			var STOPPED = DetectIfMouseStopped(event);
			if(STOPPED == 1) getMOcoordinates(event);
		}, 500);
		CURclientX = event.clientX;
		CURclientY = event.clientY;
		MOVED_TOO_FAR();
	    }
	}
}, false);



document.addEventListener("click", function(event){
	HIDE_WPT_BUBBLE(event);
});

document.addEventListener("scroll", function(event){
	HIDE_WPT_BUBBLE(event);
});



function MOVED_TOO_FAR(){
        if(shadowRoot){
		var OFFSET = 20;
	        const SL_WPToriginalText = shadowRoot.getElementById("SL_WPToriginalText");
		if(SL_WPToriginalText){
	      		if(((SHADOW_T-OFFSET) >= CURclientY || (SHADOW_B+OFFSET) <= CURclientY) || ((SHADOW_L-OFFSET) >= CURclientX || (SHADOW_R+OFFSET) <= CURclientX)) {
				HIDE_WPT_BUBBLE(WPT_GLOB_event);
			}
		}
	}
}



function getWordAtPoint(elem, x, y) {
  if(elem.nodeType == elem.TEXT_NODE) {
    var range = elem.ownerDocument.createRange();
    range.selectNodeContents(elem);
    var currentPos = 0;
    var endPos = range.endOffset;
    while(currentPos+1 < endPos) {
      range.setStart(elem, currentPos);
      range.setEnd(elem, currentPos+1);
      if(range.getBoundingClientRect().left <= x && range.getBoundingClientRect().right  >= x &&
        range.getBoundingClientRect().top  <= y && range.getBoundingClientRect().bottom >= y) {
        range.expand("sentence");
        var ret = range.toString();
        range.detach();
        return(ret);
      }
      currentPos += 1;
    }
  } else {
    for(var i = 0; i < elem.childNodes.length; i++) {
      var range = elem.childNodes[i].ownerDocument.createRange();
      range.selectNodeContents(elem.childNodes[i]);
      if(range.getBoundingClientRect().left <= x && range.getBoundingClientRect().right  >= x &&
         range.getBoundingClientRect().top  <= y && range.getBoundingClientRect().bottom >= y) {
        range.detach();
        return(getWordAtPoint(elem.childNodes[i], x, y));
      } else {
        range.detach();
      }
    }
  }
  return(null);
}  

function getWordAtPoint(elem, x, y) {
  if(elem.nodeType == elem.TEXT_NODE) {

    var range = elem.ownerDocument.createRange();
    range.selectNodeContents(elem);
    var currentPos = 0;
    var endPos = range.endOffset;

    while(currentPos+1 < endPos) {
      range.setStart(elem, currentPos);
      range.setEnd(elem, currentPos+1);
      if(range.getBoundingClientRect().left <= x && range.getBoundingClientRect().right  >= x &&
         range.getBoundingClientRect().top  <= y && range.getBoundingClientRect().bottom >= y) {
        var ret = range.toString();
        range.detach();
        return(currentPos);
      }
      currentPos += 1;
    }
  } else {
    for(var i = 0; i < elem.childNodes.length; i++) {
      var range = elem.childNodes[i].ownerDocument.createRange();
      range.selectNodeContents(elem.childNodes[i]);
      if(range.getBoundingClientRect().left <= x && range.getBoundingClientRect().right  >= x &&
         range.getBoundingClientRect().top  <= y && range.getBoundingClientRect().bottom >= y) {
        range.detach();
        return(getWordAtPoint(elem.childNodes[i], x, y));
      } else {
        range.detach();
      }
    }
  }
  return(null);
} 

function FIND_INDEX(text, pos){
    var Arr = SPLITTER(text);
    var cnt = 0;
    var index = 0;
    for (var i = 0; i < Arr.length; i++){
         if((Arr[i].length+cnt) > pos) {index = i; break;}
       	 else cnt = cnt + Arr[i].length+1;
    }
    if(Arr.length < index) index = Arr.length;
    return index;
}



function getMOcoordinates(e) {
//	try{
	    var elem = e.target; 	    
	    var cnt = 0;
	    var POS = getWordAtPoint(elem, CURclientX, CURclientY);

	    var doc = FExtension.browserInject.getDocument();
       	    RN = getRestoreNodes(doc.body);
//	    document.getSelection().removeAllRanges();    
   	    if(elem.tagName!="BODY"){
		//RICH HTML
		if(elem.childNodes.length<=1){
		    for(var i = 0; i < elem.childNodes.length; i++) {
		      var range = elem.childNodes[i].ownerDocument.createRange();			      
		      range.selectNodeContents(elem.childNodes[i]);
		      if(range.getBoundingClientRect().left <= CURclientX && range.getBoundingClientRect().right >= CURclientX && range.getBoundingClientRect().top  <= CURclientY && range.getBoundingClientRect().bottom >= CURclientY) {
	        	 range.detach();
			 var STR = String(range.startContainer.data).trim() + " ";
			 if(FIXED != STR) {
				var ALLtext = range.commonAncestorContainer.data.trim() + " ";
				var INDEX = FIND_INDEX(ALLtext, POS);
			 	FIXED=STR;
				break;
			 }
		     } else  range.detach();
		   }
		   if(STR && STR != "undefined"){
			var doc = FExtension.browserInject.getDocument();
			RN = getRestoreNodes(doc.body)
			if(RN.length>0){
			    	for (let i in RN) {
        		        	for (let restore of RN[i].nodesInfo) {
					   	var TMPnode = String(restore.result).trim() + " ";
               			   		if(STR == TMPnode) {
               		        			var ORIGINAL = GET_DATA(restore.original,INDEX);
	               		        		var TRANSLATION = GET_DATA(TMPnode,INDEX);
							clearTimeout(CheckMovement);
							SHOW_WPT_BUBBLE(ORIGINAL, TRANSLATION, range);

					   	}
				        }
        			}
			}
		    } else {
			if(SHADOW) {

			      //NOT DONE on FOXNEWS
			}
		    }
	         } else {

	           if(POS!==null){

			   var ORIG="", TRANS="";
			   if(elem.childNodes.length==1){
				var ROUTER = 10
				for(var i = 0; i < elem.childNodes.length; i++) {
					if(elem.childNodes[i].nodeName=="BR") ROUTER=0;
				}
				if(String(window.location).indexOf("wikipedia.org")!=-1 && elem.childNodes.length>ROUTER) ROUTER=1000;

				if(elem.childNodes.length<ROUTER){

				    for(var i = 0; i < elem.childNodes.length; i++) {
				      var range = elem.childNodes[i].ownerDocument.createRange();			      
				      range.selectNodeContents(elem.childNodes[i]);
			              range.detach();
				      TRANS = TRANS+ String(range.startContainer.textContent).trim() +" ";
				      var INDEX = FIND_INDEX(TRANS, POS);
				      for (let j in RN) {
        			       	for (let restore of RN[j].nodesInfo) {
					   if(restore.node.textContent.length>3){
				       	      if(range.startContainer.textContent == restore.node.textContent){
               		        		ORIG = ORIG + String(restore.node.value).trim() +" ";
               		        		ORIG = GET_DATA(ORIG,INDEX);
               		        		TRANS = GET_DATA(TRANS,INDEX);


//						 ORIG = ORIG + String(restore.node.value).trim() +" ";
//						 let selection = window.getSelection();
//						 selection.addRange(range);
					      }
					   }
	        	        	}
				      }
				    }
				    clearTimeout(CheckMovement);
				    SHOW_WPT_BUBBLE(ORIG, TRANS, range);
				} else {
				    for(var i = 0; i < elem.childNodes.length; i++) {
				      var range = elem.childNodes[i].ownerDocument.createRange();			      
				      range.selectNodeContents(elem.childNodes[i]);
				      if(range.getBoundingClientRect().left <= CURclientX && range.getBoundingClientRect().right >= CURclientX && range.getBoundingClientRect().top  <= CURclientY && range.getBoundingClientRect().bottom >= CURclientY) {
				              range.detach();
					      TRANS = TRANS + String(range.startContainer.textContent).trim() +" ";
					      var INDEX = FIND_INDEX(TRANS, POS);
					      for (let j in RN) {
        	        			for (let restore of RN[j].nodesInfo) {
						   if(restore.node.textContent.length>3){
					              if(range.startContainer.textContent == restore.node.textContent) {
               			        		ORIG = String(restore.node.value).trim() +" ";
               			        		ORIG = GET_DATA(ORIG,INDEX);
               		        			TRANS = GET_DATA(TRANS,INDEX);
						      }	
						   }
        	        			}
					      }
					      clearTimeout(CheckMovement);
					      SHOW_WPT_BUBBLE(ORIG, TRANS, range);
				     }
				  }	

				}
			   }else{
				    var ORIG="", TRANS="", SINGLE="";
				    for(var i = 0; i < elem.childNodes.length; i++) {


				      var range = elem.childNodes[i].ownerDocument.createRange();			      
				      range.selectNodeContents(elem.childNodes[i]);
			              range.detach();

				      for (let j in RN) {
        			       	for (let restore of RN[j].nodesInfo) {
					   if(restore.node.textContent.length>3){
				       	      if(range.startContainer.textContent == restore.node.textContent){
						if(SINGLE != range.startContainer.textContent){ 
						 SINGLE = range.startContainer.textContent;
					         TRANS = TRANS + String(range.startContainer.textContent).trim() +" ";
//						 ORIG = ORIG + String(restore.node.value).trim() +" ";
						 ORIG = ORIG + String(elem.childNodes[i].value).trim() +" ";
						}
					      }
					   }
	        	        	}
				      }
				    }

				    clearTimeout(CheckMovement);
				    SHOW_WPT_BUBBLE(ORIG, TRANS, range);			
			   }

		   } else {
			    var ORIG="", TRANS="", SINGLE="";
			    for(var i = 0; i < elem.childNodes.length; i++) {
			      var range = elem.childNodes[i].ownerDocument.createRange();			      
			      range.selectNodeContents(elem.childNodes[i]);
		              range.detach();
			      for (let j in RN) {
       			       	for (let restore of RN[j].nodesInfo) {
				   if(restore.node.textContent.length>3){
			       	      if(range.startContainer.textContent == restore.node.textContent){
					if(SINGLE != range.startContainer.textContent){ 
					 SINGLE = range.startContainer.textContent;
					 TRANS = TRANS + String(range.startContainer.textContent).trim() +" ";
					 ORIG = ORIG + String(restore.node.value).trim() +" ";
					}
				      }
				   }
        	        	}
			      }
			    }
			    clearTimeout(CheckMovement);
			    SHOW_WPT_BUBBLE(ORIG, TRANS, range);			
		   }
	        } 
	     } else {
		    //POOR HTML

		    for(var i = 0; i < elem.childNodes.length; i++) {
		      var range = elem.childNodes[i].ownerDocument.createRange();			      
		      range.selectNodeContents(elem.childNodes[i]);
		      if(range.getBoundingClientRect().left <= CURclientX && range.getBoundingClientRect().right >= CURclientX && range.getBoundingClientRect().top  <= CURclientY && range.getBoundingClientRect().bottom >= CURclientY) {
	        	 range.detach();
			 var STR = String(range.startContainer.data).trim() + " ";
			 if(FIXED != STR) {
//				window.getSelection().removeAllRanges();
//				e.preventDefault();
//				let selection = window.getSelection();
//				selection.addRange(range);
				var ALLrange = range.commonAncestorContainer.data.trim() + " ";
				var INDEX = FIND_INDEX(ALLrange, POS);
//				window.getSelection().removeAllRanges();
			 	FIXED=STR;
				var doc = FExtension.browserInject.getDocument();
				RN = getRestoreNodes(doc.body)
				if(RN.length>0){
				    	for (let i in RN) {
        		        		for (let restore of RN[i].nodesInfo) {
						   	var TMPnode = String(restore.result).trim() + " ";
               			   			if(STR == TMPnode) {
               		        				var ORIGINAL = GET_DATA(restore.original,INDEX);
		               		        		var TRANSLATION = GET_DATA(TMPnode,INDEX);
								clearTimeout(CheckMovement);
								SHOW_WPT_BUBBLE(ORIGINAL, TRANSLATION, range);
						   	}
					        }
	        			}
				 }
				break;
			 }
		     } else  range.detach();
		  }
	     }




//	} catch(e){}
}

function GET_DATA(text, index){
   try{
        var Arr = SPLITTER(text);
    	return Arr[index];
   } catch(ex){}
}


function SHOW_WPT_BUBBLE(TEXT, TRANSLATION, range){
 TEXT = TEXT.replace(/undefined/g,"");
 try{
//    TEXT = TEXT.replace(/(\b\S.+\b)(?=.*\1)/g, "").trim();
//    TRANSLATION = TRANSLATION.replace(/(\b\S.+\b)(?=.*\1)/g, "").trim();
    var re = new RegExp(VACINE, "g");
    TEXT = TEXT.replace(re, "");
    TEXT = TEXT.trim();
    TRANSLATION = TRANSLATION.trim();

//    if(range.startContainer.data.trim()==TRANSLATION.trim()){
	    //SELECTION
//	    let selection = document.getSelection();
//	    selection.addRange(range);
	    //SELECTION
//    }
    FIXED=""
    if(TEXT){
	TEXT = TEXT.trim().replace(/\t/g,"");
        HIDE_WPT_BUBBLE(WPT_GLOB_event);
        divElement = document.createElement("div")
        divElement.style = "all: initial;"
        divElement.classList.add("notranslate")
        divElement.id="move";
        shadowRoot = divElement.attachShadow({
        	mode: "closed"
	        })
		var OBJ = `<div id="SL_WPToriginalText" dir="auto" style="position: fixed"></div>`;
        	shadowRoot.innerHTML = DOMPurify.sanitize(OBJ);
        	{
            const style = document.createElement("style")
            style.textContent = styleTextContent
            shadowRoot.insertBefore(style, shadowRoot.getElementById("SL_WPToriginalText"))
        }

 	const SL_WPToriginalText = shadowRoot.getElementById("SL_WPToriginalText")

        SL_WPToriginalText.style.background="white";
        SL_WPToriginalText.style.color="black";
//        SL_WPToriginalText.style.fontFamily="'Helvetica', 'Arial', 'Segoe', sans-serif";

        SL_WPToriginalText.style.fontSize="14px";
        SL_WPToriginalText.style.border="1px solid grey";
        SL_WPToriginalText.style.overflow="auto";
        SL_WPToriginalText.style.padding="15px";
        SL_WPToriginalText.style.visibility="visible";
        SL_WPToriginalText.style.display="block";
        SL_WPToriginalText.style.opacity="1";
        SL_WPToriginalText.style.fontWeight="500";
        SL_WPToriginalText.style.zIndex="9999999";
        SL_WPToriginalText.style.borderRadius="5px";
        SL_WPToriginalText.style.maxWidth="75%";
        SL_WPToriginalText.style.maxHeight="25%";
        SL_WPToriginalText.style.fontStyle="normal";
        SL_WPToriginalText.style.fontVariant="normal";
        SL_WPToriginalText.style.lineHeight="normal";

        SL_WPToriginalText.innerHTML = DOMPurify.sanitize("<div id=wpt_tb></div><div id=SL_canvas>"+TEXT);

        SL_WPToriginalText.style.display='none';
        document.body.appendChild(divElement)
        SL_WPToriginalTextIsShowing = true

        const height = SL_WPToriginalText.offsetHeight
        let top = mousePos.y + 10
        top = Math.max(0, top)
        top = Math.min(window.innerHeight - height, top)
        const width = SL_WPToriginalText.offsetWidth
        let left = parseInt(mousePos.x /*- (width / 2) */ )
        left = Math.max(0, left)
        left = Math.min(window.innerWidth - width, left)
            
        SL_WPToriginalText.style.top = top + "px"
        SL_WPToriginalText.style.left = left + "px"
	SL_WPToriginalText.style.fontFamily="Arial, Georgia,Times,Times New Roman,serif";
	window.setTimeout(function() {
		    SL_WPToriginalText.style.display='block';
		    POSITIONER();
	}, 50);

	var elem = document.querySelector('#move'), 
        div = shadowRoot.querySelector('#SL_WPToriginalText'), 
	x = 0, 
        y = 0, 
        mousedown = false; 
  
 	div.addEventListener('mousedown', function (e) { 
		if(e.target.id!="SL_canvas"){
	     		mousedown = true; 
			window.setTimeout(function() {
			     	x = div.offsetLeft - e.clientX; 
     				y = div.offsetTop - e.clientY; 
			}, 5);
		}
	}, true); 
  
	div.addEventListener('mouseup', function (e) { 
	     mousedown = false; 
	}, true); 

	elem.addEventListener('mousemove', function (e) { 
	     	if (mousedown) { 
		   if(e.clientX>=0 && e.clientY>=0){
        		div.style.left = e.clientX + x + 'px'; 
         		div.style.top = e.clientY + y + 'px'; 
			WPT_Bubble_Reposition();
			e.preventDefault();
		   }
		} 
	}, true); 
     }
 } catch(ex){}
}



function POSITIONER(){
        const SL_WPToriginalText = shadowRoot.getElementById("SL_WPToriginalText");
	var W = SL_WPToriginalText.offsetWidth;
	var H = SL_WPToriginalText.offsetHeight;
        SL_WPToriginalText.style.top = (CURclientY-H-5) + "px";
        SL_WPToriginalText.style.left = (CURclientX-W/2+5) + "px";
        WPT_Bubble_Reposition();        
        SHADOW_T = SL_WPToriginalText.style.top.replace("px","");
        SHADOW_B = Math.ceil(SL_WPToriginalText.style.top.replace("px","")*1+H*1);
        SHADOW_L = SL_WPToriginalText.style.left.replace("px","");
        SHADOW_R = Math.ceil(SL_WPToriginalText.style.left.replace("px","")*1+W*1);
}

function WPT_Bubble_Reposition() {
	var doc = FExtension.browserInject.getDocument();
	var BBLdiv = shadowRoot.getElementById("SL_WPToriginalText");
	var bodyScrollTop = doc.documentElement.scrollTop || doc.body.scrollTop;
	var bodyScrollLeft = doc.documentElement.scrollLeft || doc.body.scrollLeft;
	var W = BBLdiv.offsetWidth;
	var H = BBLdiv.offsetHeight;

	var position = BBLdiv.getBoundingClientRect();
	var x = position.left;
	var y = position.top;
	var DELTAy = 1;
	if (doc.body.offsetHeight < window.innerHeight)	var DELTAy = 17;
	var DELTAx = 1;

        if(position.left<0) BBLdiv.style.left = "2px";
	var SW = window.innerWidth-18;
        if(position.right>=SW) BBLdiv.style.left = SHADOW_L+"px";
	var SH = window.innerHeight;
        if(position.top+H>=SH) BBLdiv.style.top = SHADOW_T+"px";

        if(position.top<0) BBLdiv.style.top = (position.top-position.top)+2 + "px";
	if (doc.body.offsetWidth < window.innerWidth)	var DELTAx = 17;
	if((x+BBLdiv.offsetWidth)>(bodyScrollLeft+window.innerWidth-DELTAx)){
		BBLdiv.style.left = (bodyScrollLeft+window.innerWidth-BBLdiv.offsetWidth-DELTAx) +"px";
	}

        SHADOW_T = BBLdiv.style.top.replace("px","");
        SHADOW_B = Math.ceil(BBLdiv.style.top.replace("px","")*1+H*1);
        SHADOW_L = BBLdiv.style.left.replace("px","");
        SHADOW_R = Math.ceil(BBLdiv.style.left.replace("px","")*1+W*1);

}


function HIDE_WPT_BUBBLE(e){
        if (divElement) {
		var st = WPT_IfMouseIsInside(e);
		if(st == 0){
        	    divElement.remove()
	            SL_WPToriginalTextIsShowing = false
        	}
	        clearTimeout(CheckMovement);
	}
}


function DetectIfMouseStopped(event){
	var out = 0;
                if(Math.abs(event.clientX-CURclientX)<=0 && Math.abs(event.clientY-CURclientY)<=0) {
			out=1;
			mousePos.x = event.clientX-300/2;
			mousePos.y = event.clientY-30;
		}
        return out;
}

function WPT_IfMouseIsInside(e){
	var st = 0;
        const SL_WPToriginalText = shadowRoot.getElementById("SL_WPToriginalText");
	if(SL_WPToriginalText){
		var divRect = SL_WPToriginalText.getBoundingClientRect();
		if (e.clientX >= (divRect.left-20) && e.clientX <= divRect.right && e.clientY >= divRect.top && e.clientY <= divRect.bottom) st=1;
	}
	return(st);
}

function SPLITTER(text){
     try{
	var OUT= [];
	text = text.replace(/\.\.\./g,".");

	var ABBR1="Mr.|Ms.|Mrs.|Mss.|Sen.|Rep.|D.C.|U.S.|U.S.A.|U.N.|Jan.|Feb.|Mar.|Apr.|May.|Jun.|Jul.|Aug.|Sep.|Oct.|Nov.|Dec.|Mon.|Tue.|Wed.|Thu.|Fri.|Sat.|Sun.|A.M.|P.M.|Abb.|Abf.|Abk.|Abo.|Abr.|Abs.|Abt.|Abzgl.|Acc.|Acct.|Act.|Add.|Addr.|Adj.|Adm.|Admin.|Adr.|Adv.|Ag.|Aggr.|Aka.|Alim.|Am.|Amp.|Amt.|Amtl.|Anc.|Ang.|Angl.|Ann.|Apdo.|App.|Appl.|Approc.|Approx.|Appt.|Apr.|Aprox.|Aptd.|Arg.|Arr.|Arrgmt.|Arrgt.|Artif.|Asc.|Aspt.|Ass.|Asscn.|Assmt.|Assn.|Assoc.|Asst.|Asstd.|Atm.|Att.|Attn.|Atty.|Aud.|Auj.|Aut.|Aux.";
	var ABBR2=ABBR1.toLowerCase();
	var ABBR_ARR1 = ABBR1.split("|")
	var ABBR_ARR2 = ABBR2.split("|")
	for (var a=0; a<ABBR_ARR1.length; a++){
	        var newAbbr1 = ABBR_ARR1[a].replace(/\./g,"^")
	 	text = text.replaceAll(ABBR_ARR1[a],newAbbr1);
	        var newAbbr2 = ABBR_ARR2[a].replace(/\./g,"^")
	 	text = text.replaceAll(ABBR_ARR2[a],newAbbr2);
	}

	var len = text.length;
	var newText = "";
	for (var i=0; i<len; i++){
	     var v = text.charAt(i);
	     if(v=="."){
		if (text[i-1] >= '0' && text[i-1] <= '9' && text[i+1] != " ") {
		    	v = v.replace(".","^");
		}
	     }
	     newText = newText + v;	
	}

	text = newText.replace(/\./g,".<#>");
	text = text.replace(/\!/g,"!<#>");
	text = text.replace(/\?/g,"?<#>");
	text = text.replace(/\。/g,"。<#>");
	text = text.replace(/\‧/g,"‧<#>");
	text = text.replace(/\·/g,"·<#>");
	text = text.replace(/\﹗/g,"﹗<#>");
	text = text.replace(/\！/g,"！<#>");
	text = text.replace(/\﹖/g,"﹖<#>");
	text = text.replace(/\？/g,"？<#>");
	text = text.replace(/\?/g,"?<#>");
	text = text.replace(/\^/g,".");
	var Arr = text.split("<#>");
	for(var i = 0; i < Arr.length; i++) OUT[i] = Arr[i];
	return OUT;
    } catch (ex){}	
}





