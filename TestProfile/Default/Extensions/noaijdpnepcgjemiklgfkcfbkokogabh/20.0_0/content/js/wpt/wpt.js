    var VACINE = "`ImTSL`";
    var SRL = "auto";
    var TRL = "en";
    var RESTORE = 1;
    var ACTIVATED = 0;
    var translateNodes = null
    var cnt =0;
    var prevTargetLanguage = null
    var translatedStrings = []
    var nodesTranslated = []
    var status ="prompt";
    var htmlTagsInlineText = [ '#text', 'A', 'ABBR', 'ACRONYM', 'B', 'BDO', 'BIG', 'CITE', 'DFN', 'EM', 'I', 'LABEL', 'Q', 'S', 'SMALL', 'SPAN', 'STRONG', 'SUB', 'SUP', 'U', 'TT', 'VAR']
    var htmlTagsInlineIgnore = ['BR', 'CODE', 'KBD', 'WBR' ]
    var htmlTagsNoTranslate = ['TITLE', 'SCRIPT', 'STYLE', 'svg', 'LINK']
    var SHADOW = "";
    var restoreSHADOWnodes = []
    var originalPageTitle = null
    var translatedAttributes = []
    var translateNewNodesTimer = null
    var newNodesToTranslate = []
    var NestedNodes = []
    var NestedStrings = []
    var removedNodes = []
    var restoreNodes = []
    var FIRSTRUN = 0;
    var KUKLA = []
    var NodesTimerHandler = "";
    var newNodes = []
    var LASTorig="";
    var RUNTIME_PACKAGE = [];
    var WPT_PREVIOUS="";
    var DETECTED="";
    // TB
    var	SL_LOC="en";
    var SL_LNG_CUSTOM_LIST="";
    var SL_FAV_START="3";
//    var SL_FAV_MAX="10";
    var SL_FAV_MAX="1000";
    var SL_FAV_LANGS_WPT="";
    var WPTdstlang="";
    // TB
    var SegmentsToTranslate = null
    var	BaseGTK = "451769.3009291968"
    var TEMP_SECTOR_CONTENT = []
    //Init TB
    try {
      originalPageTitle = document.title;
      FExtension.browserInject.extensionSendMessage({greeting: 1}, function(response) {
	if(response && response.farewell){
		var theresponse = response.farewell.split("~");
		WPTdstlang=theresponse[20];


		var tmpl=theresponse[82];
		if(tmpl.indexOf(",")!=-1){
			var tmpl2 = tmpl.split(",");
			WPTdstlang = tmpl2[0];
		} else {
			WPTdstlang = tmpl;
		}
		TRL = WPTdstlang;

		SL_LOC=theresponse[22];
		SL_LNG_CUSTOM_LIST=theresponse[29];
		SL_FAV_LANGS_WPT=theresponse[82];
		INIT_WPT_TB(SL_LOC,1);
	}
      });
    } catch (ex){}



    window.addEventListener('load', function (event) {		        
	LINKS_HANDLER();
    }, false);


    var SLmutationObserver = new MutationObserver(function (mutations) {

        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(addedNode => {
                if (htmlTagsNoTranslate.indexOf(addedNode.nodeName) == -1) {
                    if (htmlTagsInlineText.indexOf(addedNode.nodeName) == -1) {
                        if (htmlTagsInlineIgnore.indexOf(addedNode.nodeName) == -1) {
                            translateNodes.push(addedNode)
                        }
                    }
                }
            })
            mutation.removedNodes.forEach(removedNode => {
                removedNodes.push(removedNode)
            })
        })
  
        translateNodes.forEach(ptt => {
            if (newNodes.indexOf(ptt) == -1) {
                newNodes.push(ptt)
            }
        })
    })



    function enableMutatinObserver() {
            disableMutatinObserver();
	    WPT_RUN();	

/*
//            NodesTimerHandler = setInterval(WPT_TRANSLATOR, 2000);
            NodesTimerHandler = setInterval(WPT_RUN, 2000);
//            NodesTimerHandler = setInterval(WPT_MUTATION, 2000);

            SLmutationObserver.observe(document.body, {
                childList: true,
                subtree: true
            })
*/ 

    }

    function disableMutatinObserver() {
        clearInterval(NodesTimerHandler);
        newNodes = [];
        removedNodes = [];
        SLmutationObserver.disconnect();
        SLmutationObserver.takeRecords();
    }


    function WPT_INIT(){	
	if(RESTORE==0){
		if(self == top ) {
		enableMutatinObserver();
		getPiecesToTranslate(root = document.body, 0);
		}
	}
    }	    
            
	

function documentHasShadowRoot(root = document) {
    // Get all elements in the current root
    const elements = root.querySelectorAll('*');

    for (const el of elements) {
        // If element has an open shadow root
        if (el.shadowRoot instanceof ShadowRoot) {
            return 1;
        }
        // If element has a shadow root, search inside it recursively
        if (el.shadowRoot) {
            if (documentHasShadowRoot(el.shadowRoot)) {
                return 1;
            }
        }
    }
    return 0;
}


 
    function WPT_RUN(){
	if(RESTORE==0){	    
//---------------------------------------IF SHADOW
	    var rt = documentHasShadowRoot(root = document);
	    if(rt==1)   getPiecesToTranslate(root = document.body, 0);
//---------------------------------------IF SHADOW
	    ACTIVATED=1;
            TRL = WPTdstlang;
            //SRL = WPTsrclang;
	    SRL = "auto";
	    var doc = FExtension.browserInject.getDocument();
		    if(doc.getElementsByTagName('html')[0].lang == "ja"){
			doc.getElementsByTagName('html')[0].lang="";
			var divs = doc.getElementsByTagName('div');
			for(d=0; d<divs.length; d++){
				divs[d].lang="";
			}
		    }
	            translateNodes = getTranslateNodes(root = doc.body)
		    TEMP_SECTOR_CONTENT=[];
	            for (let i in translateNodes) {
		    	var SegmentsToTranslate="";
                	for (let nodeInfo of translateNodes[i].nodesInfo) {

	                    //nodesTranslated.push({node: nodeInfo.node, original: nodeInfo.node.textContent})	                    
			    //restoreNodes[i]=nodeInfo.node.textContent;
			    var rect = isInViewport(translateNodes[i].parent, doc);

			    if (rect == true){
				var row = nodeInfo.node.textContent.replace(/<[^>]*>/ig,"");
				var newrow = row.replace(/\"/g,'\\"')
				newrow = newrow.replace(/\|/g,' | ')
				newrow = newrow.replace(/\+/g,' ')
				if(newrow != ""){
					SegmentsToTranslate = newrow.trim()

					if(SegmentsToTranslate!="") {
						//Skips all digits, time, and date
						var tmp = SegmentsToTranslate.replace(":","");
						tmp = tmp.replace("/","");
						tmp = tmp.replace("-","");
						tmp = tmp.replace("|","");
						var STRobj = isNaN(tmp);

						if(STRobj===true){
							var IFTRANSLATED = CHECK_IF_ALREADY_TRANSLATED(nodeInfo.node);
							if(IFTRANSLATED==0){
                                        			TEMP_SECTOR_CONTENT.push({content: SegmentsToTranslate, node: nodeInfo.node});
								RUNTIME_PACKAGE.push({node: nodeInfo, original: SegmentsToTranslate});
							}
						}
					}
				}
			    }
        	        }
	            }

//		    WP_SECTOR_TRANSLATE();

		    WP_TRANSLATE_PACKAGE();

//		    if(TranslatorIM.SL_WPT_METHOD==1) WP_TRANSLATE_PACKAGE(); 
		    
                    WP_TRANSLATE_ATTR();
	} else disableMutatinObserver();

    }

    function getPiecesToTranslate(root = document.body, st) {

        let index = 0
        let currentParagraphSize = 0
        const getAllNodes = function (node, lastHTMLElement = null, st) {

            if (node.nodeType == 1 || node.nodeType == 11) {
                if (node.nodeType == 11) {
                    lastHTMLElement = node.host
                } else if (node.nodeType == 1) {
                    lastHTMLElement = node
                    if (htmlTagsInlineIgnore.indexOf(node.nodeName) !== -1 ||
                        htmlTagsNoTranslate.indexOf(node.nodeName) !== -1 ||
                        node.classList.contains("notranslate") ||
                        node.getAttribute("translate") === "no" ||
                        node.isContentEditable) {
                    }
                }
                function getAllChilds(childNodes, st) {
		    var doc = FExtension.browserInject.getDocument();
                    Array.from(childNodes).forEach(_node => {
                        if (_node.nodeType == 1) {
                            lastHTMLElement = _node
                        }
                        if (htmlTagsInlineText.indexOf(_node.nodeName) == -1) {
                            getAllNodes(_node, lastHTMLElement, st)
                        } else {
                            getAllNodes(_node, lastHTMLElement, st)
				if(st==1){
			            translateNodes = getTranslateNodes(lastHTMLElement)
	        		    for (let i in translateNodes) {
				    	var SegmentsToTranslate="";
                			for (let nodeInfo of translateNodes[i].nodesInfo) {
					    var rect = isInViewport(translateNodes[i].parent, doc);
					    if (rect == true){
						var row = nodeInfo.node.textContent.replace(/<[^>]*>/ig,"");
						var newrow = row.replace(/\"/g,'\\"')
						newrow = newrow.replace(/\|/g,' | ')
						newrow = newrow.replace(/\+/g,' ')
						if(newrow != ""){
							SegmentsToTranslate = newrow.trim()
							if(SegmentsToTranslate!="") {					               		
								    if(CHECK_IF_ALREADY_TRANSLATED(nodeInfo)==0){
									RUNTIME_PACKAGE.push({node: nodeInfo, original: SegmentsToTranslate});
                                      			                restoreSHADOWnodes.push({node: nodeInfo.node, original: nodeInfo.node.textContent});
								    }
							}
						}
					    }	
        			        }
			            }

//                                    if(SHADOW) WP_TRANSLATE_PACKAGE();
				    
				}
                        }
                    })
                }

                getAllChilds(node.childNodes,st)
                if (node.shadowRoot) {
                    SHADOW = node.shadowRoot;
                    getAllChilds(node.shadowRoot.childNodes,1)
                }

            } else if (node.nodeType == 3) {
                if (node.textContent.trim().length > 0) {		    
                    currentParagraphSize += node.textContent.length
                }
            }
        }
        getAllNodes(root)
    }


  function getPiecesToTranslate__(root = document.documentElement) {
    const piecesToTranslate = [
      {
        isTranslated: false,
        parentElement: null,
        topElement: null,
        bottomElement: null,
        nodes: [],
      },
    ];
    let index = 0;
    let currentParagraphSize = 0;

    const getAllNodes = function (
      node,
      lastHTMLElement = null,
      lastSelectOrDataListElement = null
    ) {
      if (node.nodeType == 1 || node.nodeType == 11) {
        if (node.nodeType == 11) {
          lastHTMLElement = node.host;
          lastSelectOrDataListElement = null;
        } else if (node.nodeType == 1) {
          lastHTMLElement = node;
          const nodeName = node.nodeName.toLowerCase();

          if (nodeName === "select" || nodeName === "datalist")
            lastSelectOrDataListElement = node;

          if (
            htmlTagsInlineIgnore.indexOf(nodeName) !== -1 ||
            isNoTranslateNode(node) ||
            node.classList.contains("notranslate") ||
            node.getAttribute("translate") === "no" ||
            node.isContentEditable ||
            node.classList.contains("material-icons") || 
            node.classList.contains("material-symbols-outlined") ||
            nodeName.startsWith("br-") || 
            node.getAttribute("id") === "branch-select-menu" || 
            (location.hostname === "twitter.com" &&
              nodeName === "a" &&
              (node.matches ? node.matches("article a") : true)) 
          ) {
            if (piecesToTranslate[index].nodes.length > 0) {
              currentParagraphSize = 0;
              piecesToTranslate[index].bottomElement = lastHTMLElement;
              piecesToTranslate.push({
                isTranslated: false,
                parentElement: null,
                topElement: null,
                bottomElement: null,
                nodes: [],
              });
              index++;
            }
            return;
          }
        }

        function getAllChilds(childNodes) {
          Array.from(childNodes).forEach((_node) => {
            const nodeName = _node.nodeName.toLowerCase();

            if (_node.nodeType == 1) {
              lastHTMLElement = _node;
              if (nodeName === "select" || nodeName === "datalist")
                lastSelectOrDataListElement = _node;
            }

            if (htmlTagsInlineText.indexOf(nodeName) == -1) {
              if (piecesToTranslate[index].nodes.length > 0) {
                currentParagraphSize = 0;
                piecesToTranslate[index].bottomElement = lastHTMLElement;
                piecesToTranslate.push({
                  isTranslated: false,
                  parentElement: null,
                  topElement: null,
                  bottomElement: null,
                  nodes: [],
                });
                index++;
              }

              getAllNodes(_node, lastHTMLElement, lastSelectOrDataListElement);

              if (piecesToTranslate[index].nodes.length > 0) {
                currentParagraphSize = 0;
                piecesToTranslate[index].bottomElement = lastHTMLElement;
                piecesToTranslate.push({
                  isTranslated: false,
                  parentElement: null,
                  topElement: null,
                  bottomElement: null,
                  nodes: [],
                });
                index++;
              }
            } else {
              getAllNodes(_node, lastHTMLElement, lastSelectOrDataListElement);
            }
          });
        }

        getAllChilds(node.childNodes);
        if (!piecesToTranslate[index].bottomElement) {
          piecesToTranslate[index].bottomElement = node;
        }
        if (node.shadowRoot) {
          getAllChilds(node.shadowRoot.childNodes);
          if (!piecesToTranslate[index].bottomElement) {
            piecesToTranslate[index].bottomElement = node;
          }
        }
      } else if (node.nodeType == 3) {
        if (node.textContent.trim().length > 0) {
          if (!piecesToTranslate[index].parentElement) {
            if (
              node &&
              node.parentNode &&
              node.parentNode.nodeName.toLowerCase() === "option" &&
              lastSelectOrDataListElement
            ) {
              piecesToTranslate[index].parentElement =
                lastSelectOrDataListElement;
              piecesToTranslate[index].bottomElement =
                lastSelectOrDataListElement;
              piecesToTranslate[index].topElement = lastSelectOrDataListElement;
            } else {
              let temp = node.parentNode;
              const nodeName = temp.nodeName.toLowerCase();
              while (
                temp &&
                temp != root &&
                (htmlTagsInlineText.indexOf(nodeName) != -1 ||
                  htmlTagsInlineIgnore.indexOf(nodeName) != -1)
              ) {
                temp = temp.parentNode;
              }
              if (temp && temp.nodeType === 11) {
                temp = temp.host;
              }
              piecesToTranslate[index].parentElement = temp;
            }
          }
          if (!piecesToTranslate[index].topElement) {
            piecesToTranslate[index].topElement = lastHTMLElement;
          }
          if (currentParagraphSize > 1000) {
            currentParagraphSize = 0;
            piecesToTranslate[index].bottomElement = lastHTMLElement;
            const pieceInfo = {
              isTranslated: false,
              parentElement: null,
              topElement: lastHTMLElement,
              bottomElement: null,
              nodes: [],
            };
            pieceInfo.parentElement = piecesToTranslate[index].parentElement;
            piecesToTranslate.push(pieceInfo);
            index++;
          }
          currentParagraphSize += node.textContent.length;
          piecesToTranslate[index].nodes.push(node);
          piecesToTranslate[index].bottomElement = null;
        }
      }
    };
    getAllNodes(root);

    if (
      piecesToTranslate.length > 0 &&
      piecesToTranslate[piecesToTranslate.length - 1].nodes.length == 0
    ) {
      piecesToTranslate.pop();
    }

    return piecesToTranslate;
  }




    function isInViewport (elem, doc ) {
	try{
		var distance = elem.getBoundingClientRect();
	        if ((distance.top >= 0 && distance.top <= (window.innerHeight+15000)) || (distance.bottom >= 0 && distance.bottom <= (window.innerHeight+15000))) {
	//          if ((distance.top > 0 && distance.top <= window.innerHeight) || (distance.bottom > 0 && distance.bottom <= window.innerHeight)) {
        	   return true;
		}
	} catch (ex){return true;}
    }



    function WPT(st, host){
	RESTORE=0;	
	//WPT_RUN();		
	chrome.runtime.sendMessage({greeting: "ACT_ST:>"+st+","+host}, function(response) {}); 		
    }



 


    function getTranslateNodes(node) {

        var translateNodes = [{isTranslated: false, parent: null, nodesInfo: []}]
        var index = 0
        var getAllNodes = function (node, lastHTMLElement) {
            if (node.nodeType == 1 && htmlTagsInlineIgnore.indexOf(node.nodeName) == -1
            && !node.classList.contains("notranslate") && !node.isContentEditable) {
                if (translateNodes[index].nodesInfo.length > 0 && htmlTagsInlineText.indexOf(node.nodeName) == -1) {
                    translateNodes.push({isTranslated: false, parent: null, nodesInfo: []})
                    index++
                }


                if (htmlTagsNoTranslate.indexOf(node.nodeName) == -1) {
                    Array.from(node.childNodes).forEach(value => {
                        getAllNodes(value)
                    })
/*
                    Array.from(node.childNodes).forEach(_node => {

                        if (_node.nodeType == 1) {
                            lastHTMLElement = _node
                        }
                        if (htmlTagsInlineText.indexOf(_node.nodeName) == -1) {
                            getAllNodes(_node, lastHTMLElement)
                        } else {
                            getAllNodes(_node, lastHTMLElement)
		       }
                    })
*/
                }

            } else if (node.nodeType == 3) {
                if (node.textContent.trim().length > 0) {
                    if (!translateNodes[index].parent) {
                        var temp = node.parentNode
                        while (temp && temp != document.body && (htmlTagsInlineText.indexOf(temp.nodeName) != -1 || htmlTagsInlineIgnore.indexOf(temp.nodeName) != -1)) {
                            temp = temp.parentNode
                        }
                        translateNodes[index].parent = temp
                    }
                    translateNodes[index].nodesInfo.push({node: node, textContent: node.textContent, original: node.value})

                }
            }
        }

        

        getAllNodes(node)


        if (translateNodes.length > 0 && translateNodes[translateNodes.length-1].nodesInfo.length == 0) {
            translateNodes.pop()
        }
        return translateNodes;
    }




    function getRestoreNodes(node) {
        var translateNodes = [{isTranslated: false, parent: null, nodesInfo: []}]
        var index = 0
        var getAllNodes = function (node) {
            if (node.nodeType == 1 && htmlTagsInlineIgnore.indexOf(node.nodeName) == -1
            && !node.classList.contains("notranslate") && !node.isContentEditable) {
                if (translateNodes[index].nodesInfo.length > 0 && htmlTagsInlineText.indexOf(node.nodeName) == -1) {
                    translateNodes.push({isTranslated: false, parent: null, nodesInfo: []})
                    index++
                }

                if (htmlTagsNoTranslate.indexOf(node.nodeName) == -1) {
                    Array.from(node.childNodes).forEach(value => {
                        getAllNodes(value)
                    })
                }
            } else if (node.nodeType == 3) {
                if (node.textContent.trim().length > 0) {
                    if (!translateNodes[index].parent) {
                        var temp = node.parentNode
                        while (temp && temp != document.body && (htmlTagsInlineText.indexOf(temp.nodeName) != -1 || htmlTagsInlineIgnore.indexOf(temp.nodeName) != -1)) {
                            temp = temp.parentNode
                        }
                        translateNodes[index].parent = temp
                    }
                    translateNodes[index].nodesInfo.push({node: node, result: node.textContent, original: node.value})
                }
            }
        }

        

        getAllNodes(node)

        if (translateNodes.length > 0 && translateNodes[translateNodes.length-1].nodesInfo.length == 0) {
            translateNodes.pop()
        }
        return translateNodes;
    }








    function gettranslatedAttributes(root = document.body) {
        const translatedAttributes = []
        

        const placeholdersElements = root.querySelectorAll('input[placeholder], textarea[placeholder]')
        const altElements = root.querySelectorAll('area[alt], img[alt], input[type="image"][alt]')
        const valueElements = root.querySelectorAll('input[type="button"], input[type="submit"]')
        const titleElements = root.querySelectorAll("body [title]")
        
        function hasNoTranslate(elem) {
            if (elem && (elem.classList.contains("notranslate") || elem.getAttribute("translate") === "no")) {
                return true
            }
        }

        placeholdersElements.forEach(e => {
            if (hasNoTranslate(e)) return;
            
            const txt = e.getAttribute("placeholder")
            if (txt && txt.trim()) {
                translatedAttributes.push({
                    node: e,
                    original: txt,
                    attrName: "placeholder"
                })
            }
        })
        
        altElements.forEach(e => {
            if (hasNoTranslate(e)) return;
            
            const txt = e.getAttribute("alt")
            if (txt && txt.trim()) {
                translatedAttributes.push({
                    node: e,
                    original: txt,
                    attrName: "alt"
                })
            }
        })
        

        valueElements.forEach(e => {
            if (hasNoTranslate(e)) return;
            const txt = e.getAttribute("value")
            if (e.type == "submit" && !txt) {
                translatedAttributes.push({
                    node: e,
                    original: "Submit Query",
                    attrName: "value"
                })
            } else if (txt && txt.trim()) {
                translatedAttributes.push({
                    node: e,
                    original: txt,
                    attrName: "value"
                })
            }
        })
        
        titleElements.forEach(e => {
            if (hasNoTranslate(e)) return;
            
            const txt = e.getAttribute("title")
            if (txt && txt.trim()) {
                translatedAttributes.push({
                    node: e,
                    original: txt,
                    attrName: "title"
                })
            }
        })
        
        return translatedAttributes
    }


    function WP_TRANSLATE_ATTR(){           
    	try{
	        translatedAttributes = gettranslatedAttributes();
		if(translatedAttributes.length>0){
			var IFTRANSLATED = 0;
	                var T = "", rT = "";
			for(var x = 0; x < translatedAttributes.length; x++){
			    	rT = rT + translatedAttributes[x].original;
				T = T+"&q="+encodeURIComponent(translatedAttributes[x].original);
				IFTRANSLATED = IFTRANSLATED+CHECK_IF_ALREADY_TRANSLATED(translatedAttributes[x].node);

	            	    	var thezip = translatedAttributes[x];
			    	if(thezip.attrName == "placeholder") thezip.original = thezip.node.placeholder; 
			    	else thezip.original = thezip.node.value;

			}

       			if(IFTRANSLATED==0){
				var tk = GetHash(rT,BaseGTK);
				baseUrl = "https://translate.googleapis.com/translate_a/t?anno=3&client=te&v=1.0&format=html&sl="+SRL+"&tl="+TRL+"&tk="+tk;
	        	        var ajaxRequest = new XMLHttpRequest();
				ajaxRequest.onreadystatechange = function() {
				    if (this.readyState == 4 && this.status == 200) {
        	        	            var RESP = this.response;
        	        	            var PLACER="";
					    if(RESP){
						    PLACER = RESP[0];
						    for(var x = 0; x < RESP.length; x++){
							    PLACER = RESP[x][0];
						            const attr = translatedAttributes[x];
							    if(PLACER && attr.attrName == "placeholder") {
								if(attr.original!=""){
									attr.node.placeholder=PLACER;
									nodesTranslated.push({node: attr.node, result: PLACER});
								}
							    } else {
								if(attr.original!=""){
									attr.node.setAttribute(attr.attrName, PLACER);
									attr.node.value=PLACER;
									nodesTranslated.push({node: attr.node, result: PLACER});
								}
							    }
						    }
                        		    }
				    }
				};
	        	        ajaxRequest.open("POST", baseUrl, true);
				ajaxRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	                	ajaxRequest.responseType = "json";
		                ajaxRequest.send(T)		
			}
		}

	} catch(ex){}
     }

     function CHECK_IF_ALREADY_TRANSLATED(n){
	var OUT = 0;
           for(var i=0; i<nodesTranslated.length; i++){
                if(n.textContent==nodesTranslated[i].result) {
			if(nodesTranslated.length==0) OUT=2;
			else{
				//console.log(n.textContent+"=="+nodesTranslated[i].result)
				OUT = 1; 
			}
			break;
		}
	   }
	return OUT;
     }

     function WP_SECTOR_TRANSLATE(){

	var realTEXT="";
	var TEXT="";             
	for(var i=0; i < TEMP_SECTOR_CONTENT.length; i++){
		        var CNT = TEMP_SECTOR_CONTENT[i].content;
            		var SEG1 = CNT;
	       	  	realTEXT = realTEXT+SEG1;
            		var SEG2 = encodeURIComponent(SEG1);
	       		TEXT = TEXT+"&q="+SEG2;
	}
	if(i>0){
		var tk = GetHash(realTEXT,BaseGTK);
		var baseUrl = "https://translate.googleapis.com/translate_a/t?anno=3&client=te&v=1.0&format=html&sl="+SRL+"&tl="+TRL+"&tk="+tk;
                var ajaxRequest = new XMLHttpRequest();
		ajaxRequest.onreadystatechange = function() {
		    if (this.readyState == 4 && this.status == 200) {
                        var result = this.response;
			for(var j=0; j < result.length; j++){
	                        var res = String(result[j][0])+" ";
			        res = res.replace(/\"/g, '&quot;').replace(/\'/g, "&#39;");
			        res = res.replace(/\ "/g, '&quot;').replace(/\ '/g, "&#39;");
			        res = res.replace(/&nbsp;/g, ' ');
	                	if (res.indexOf("<pre") !== -1) {
                        		res = res.replace("</pre>", "")
	                        	const index = res.indexOf(">")
        	                	res = res.slice(index + 1)
				}
	                	const sentences = []

	        	        let idx = 0
		                while (true) {
                	        	const sentenceStartIndex = res.indexOf("<b>", idx)
                        		if (sentenceStartIndex === -1) break;

                        		const sentenceFinalIndex = res.indexOf("<i>", sentenceStartIndex)

	                        	if (sentenceFinalIndex === -1) {
        	                    		sentences.push(res.slice(sentenceStartIndex + 3))
                	            		break
                        		} else {
                            			sentences.push(res.slice(sentenceStartIndex + 3, sentenceFinalIndex))
	                        	}
	                        	idx = sentenceFinalIndex
        		       	}

				if(res.indexOf('</a>,')!=-1){
					var TMP = res.split('</a>,');
					res = TMP[0]+"</a>";
					if(DETECTED=="") DETECTED = TMP[1];
				}

                    		res = sentences.length > 0 ? sentences.join(" ") : res;
			    	res = String(res).replace(/<[^>]*>?/g,' ');
			    	res = unescSPEC(res);


                	    	if(res){	
					var TMP="";
                         		if(TEMP_SECTOR_CONTENT[j].node.textContent != res) TMP = TEMP_SECTOR_CONTENT[j].node.textContent;
			 	 	nodesTranslated.push({node: TEMP_SECTOR_CONTENT[j].node, result: res});
					if(TMP!="") {
					 	TEMP_SECTOR_CONTENT[j].node.textContent = res;
					 	TEMP_SECTOR_CONTENT[j].node.value=TMP;
					}
			    	}
			}
		  }
		};
                ajaxRequest.open("POST", baseUrl, true);
		ajaxRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                ajaxRequest.responseType = "json";
                ajaxRequest.send(TEXT)

	}
     }



     function WP_TRANSLATE(TEXT, n, st){
	TEXT = TEXT.replace(/\t+/g, "");
	TEXT = TEXT.replace(/\s+/g, ' ').trim();
	var IFTRANSLATED = CHECK_IF_ALREADY_TRANSLATED(n);
	//Skips all digits, time, and date
	var tmp = TEXT.replace(":","");
	tmp = tmp.replace("/","");
	tmp = tmp.replace("-","");
	var STRobj = isNaN(tmp);
	if(STRobj===false) IFTRANSLATED=1; 
	//--------------------------------

	if(IFTRANSLATED == 0){
	   TEXT = TEXT.trim();
	   var tmp = TEXT.substr(5,2);

           if(encodeURIComponent(TEXT).length < 1) {
             if(tmp.indexOf(":/")==-1){  

	    	TEXT = TEXT.replace(/\. /g, "~")
	    	TEXT = TEXT.replace(/\?/g, "*")
	    	TEXT = TEXT.replace(/\!/g, "^")
	    	TEXT = TEXT.replace(/\&\#39;/g, "'")
	    	TEXT = TEXT.replace(/\&\# 39;/g, "'")

		var realTEXT=TEXT;

		TEXT = "&q="+encodeURIComponent(TEXT);
		
		var tk = GetHash(realTEXT,BaseGTK);

		baseUrl = "https://translate.googleapis.com/translate_a/t?anno=1&client=te&v=1.0&format=html&sl="+SRL+"&tl="+TRL+"&tk="+tk;
                var ajaxRequest = new XMLHttpRequest();
		ajaxRequest.onreadystatechange = function() {
		    if (this.readyState == 4 && this.status == 200) {
                            const response = this.response;
                            var responseJson;
                            if (typeof response[0] == "string") responseJson = response[0]
                            else responseJson = response.map(value => value[0])

                            if(SRL!="auto") responseJson = response.replace(/<[^>]*>?/g,' ');
			    else responseJson = responseJson.replace(/<[^>]*>?/g,' ');

			    responseJson = responseJson + " "; 
			    responseJson = responseJson.replace(/\ ~/g, ". ")
			    responseJson = responseJson.replace(/\~/g, ". ")
			    responseJson = responseJson.replace(/\*/g, "? ")
			    responseJson = responseJson.replace(/\^/g, "! ")
			    responseJson = responseJson.replace(/&#39;/g, "'")
			    responseJson = responseJson.replace(/&nbsp;/g, " ")

			    responseJson = responseJson.replace(/&amp;/g, "&")
			    responseJson = responseJson.replace(/\\ &quot;/g, '"')
			    responseJson = responseJson.replace(/\\&quot;/g, '"')
			    responseJson = responseJson.replace(/\&quot;/g, '"')
			    responseJson = responseJson.replace(/\\"/g, '"')
                            if(responseJson){	
				 var TMP="";
        	                 if(n.textContent != responseJson) TMP = n.textContent;
			 	 nodesTranslated.push({node: n, result: responseJson});
			 	 //translateNodes.push({node: n, result: responseJson, original: TMP});
				 n.textContent = responseJson;
				 n.value=TMP;
			    }
		    }
		};
                ajaxRequest.open("POST", baseUrl, true);
		ajaxRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                ajaxRequest.responseType = "json";
                ajaxRequest.send(TEXT)
	     }
	   } else {
	      if(TEXT!=LASTorig){
		if (st==1) LASTorig = TEXT;
		var realTEXT="";
//	    	TEXT = TEXT.replace(/\./g,"</a>.<a>")
//	    	TEXT = TEXT.replace(/\?/g,"</a>?<a>")
//	    	TEXT = TEXT.replace(/\!/g,"</a>!<a>")
//            	TEXT = "<pre><a>" + TEXT + "</pre>";
            	TEXT = "<pre><a>" + TEXT + "</a></pre>";
          	realTEXT = TEXT;

		TEXT = encodeURIComponent(TEXT);
		TEXT = "&q="+TEXT;
		var tk = GetHash(realTEXT,BaseGTK);
		var baseUrl = "https://translate.googleapis.com/translate_a/t?anno=2&client=te&v=1.0&format=html&sl="+SRL+"&tl="+TRL+"&tk="+tk;

                var ajaxRequest = new XMLHttpRequest();
		ajaxRequest.onreadystatechange = function() {
		    if (this.readyState == 4 && this.status == 200) {
                        var result = String(this.response[0]);

		        result = result.replace(/\"/g, '&quot;').replace(/\'/g, "&#39;");
		        result = result.replace(/\ "/g, '&quot;').replace(/\ '/g, "&#39;");
		        result = result.replace(/&nbsp;/g, ' ');
	                if (result.indexOf("<pre") !== -1) {
                        	result = result.replace("</pre>", "")
                        	const index = result.indexOf(">")
                        	result = result.slice(index + 1)
			}
	                const sentences = []

        	        let idx = 0
	                while (true) {
                        	const sentenceStartIndex = result.indexOf("<b>", idx)
                        	if (sentenceStartIndex === -1) break;

                        	const sentenceFinalIndex = result.indexOf("<i>", sentenceStartIndex)

                        	if (sentenceFinalIndex === -1) {
                            		sentences.push(result.slice(sentenceStartIndex + 3))
                            		break
                        	} else {
                            		sentences.push(result.slice(sentenceStartIndex + 3, sentenceFinalIndex))
                        	}
                        	idx = sentenceFinalIndex
                    	}

			if(result.indexOf('</a>,')!=-1){
				var TMP = result.split('</a>,');
				result = TMP[0]+"</a>";
				if(DETECTED=="") DETECTED = TMP[1];
			}

                    	result = sentences.length > 0 ? sentences.join(" ") : result;
		    	result = String(result).replace(/<[^>]*>?/g,' ');
		    	result = unescSPEC(result);


                    	if(result){	
				var TMP="";
                         	if(n.textContent != result) TMP = n.textContent;
		 	 	nodesTranslated.push({node: n, result: result});
				if(TMP!="") {
		//		 	translateNodes.push({node: n, result: result, original: TMP});
				 	n.textContent = result;
				 	n.value=TMP;
				}
		    	}
		  }
		};
                ajaxRequest.open("POST", baseUrl, true);
		ajaxRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                ajaxRequest.responseType = "json";
                ajaxRequest.send(TEXT)
             }
           }

        } 
    }


    function unescSPEC(text) {
        return text
            .replace(/\&amp;/g, "&")
            .replace(/\&lt;/g, "<")
            .replace(/\&gt;/g, ">")
            .replace(/\\ &quot;/g, '"')
            .replace(/\\&quot;/g, '"')
            .replace(/\&quot;/g, '"')
            .replace(/\"/g, '"')
            .replace(/\\"/g, '"')
            .replace(/\\\"/g, '"')
            .replace(/\&#39;/g, "'")
            .replace(/\''/g, '"')
	    .replace(/\``/g, '"')
	    .replace(/\" /g, '"');


    }




    function Shifter(n, str) {
        	for (var i = 0; i < str.length - 2; i += 3) {
	            var acc = str.charAt(i + 2);
        	    if ('a' <= acc) acc = acc.charCodeAt(0) - 87;
	            else acc = Number(acc);
        	    if (str.charAt(i + 1) == '+') acc = n >>> acc;
	            else acc = n << acc;
        	    if (str.charAt(i) == '+') n += acc & 4294967295;
	            else n ^= acc;
        	}
	        return n;
     }

     function TQmaker(q) {
	        var bArr = [], idx = [];
	        for (var i = 0; i < q.length; i++) {
        	    var CC = q.charCodeAt(i);
	            if (128 > CC) bArr[idx++] = CC;
        	    else {
                	if (2048 > CC) bArr[idx++] = CC >> 6 | 192;
	                else {
        	            if (55296 == (CC & 64512) && i + 1 < q.length && 56320 == (q.charCodeAt(i + 1) & 64512)) {
                	        CC = 65536 + ((CC & 1023) << 10) + (q.charCodeAt(++i) & 1023);
                        	bArr[idx++] = CC >> 18 | 240;
	                        bArr[idx++] = CC >> 12 & 63 | 128;
        	            } else bArr[idx++] = CC >> 12 | 224;
                	    bArr[idx++] = CC >> 6 & 63 | 128;
	                }
        	        bArr[idx++] = CC & 63 | 128;
	            }
        	}
	        return bArr;
     }

     function GetHash(q, w) {
	        var SplTK = w.split('.');
        	var indTK = Number(SplTK[0]) || 0;
	        var TK = Number(SplTK[1]) || 0;
        	var bArr = TQmaker(q);
	        var TMPr = indTK;
        	for (var i = 0; i < bArr.length; i++) {
	            TMPr += bArr[i];
        	    TMPr = Shifter(TMPr, '+-a^+6');
	        }
        	TMPr = Shifter(TMPr, '+-3^+b+-f');
	        TMPr ^= TK;
        	if (TMPr <= 0) TMPr = (TMPr & 2147483647) + 2147483648;
	        var Out = TMPr % 1000000;
        	return Out.toString() + '.' + (Out ^ indTK);
    }


    function LINKS_HANDLER(){
	    setTimeout(function() {
	    	try{
	//	   if(self==top){
			var H = top.location.host;
			if(H == TranslatorIM.SL_WPT_ACT_URL){
			  	var st = 1;
				chrome.runtime.sendMessage({greeting: "ACT_ST:>"+st+","+H}, function(response) {});				
			}
	//	   } 
    		} catch (ex){}	
	    }, 150);
    }

    function RESTORE_TITLE(){
       document.title = originalPageTitle;
    }

    function WPT_RESTORE_ORIGINAL_NODES(){
	RESTORE_TITLE();
    	RESTORE=1;
        //Restore ROOT
       	var doc = FExtension.browserInject.getDocument();
       	RN = getRestoreNodes(doc.body)
	if(RN.length>0){
            for (let i in RN) {
                for (let restore of RN[i].nodesInfo) {
                   if(restore.node.value){
			restore.node.replaceWith(restore.node.value.replace(VACINE,""));
                        restore.node.value="";
		   }
                }
            }
	}
        nodesTranslated = []

        //Restore ATTRIBUTES
        translatedAttributes = gettranslatedAttributes(doc.body);
	if(translatedAttributes.length>0){
            for (let j in translatedAttributes) {
		if(translatedAttributes[j].attrName=="placeholder") translatedAttributes[j].node.placeholder=translatedAttributes[j].node.ariaLabel;
		if(translatedAttributes[j].attrName=="value") translatedAttributes[j].node.value=translatedAttributes[j].original;
            }
	}
        translatedAttributes = []

        //Restore HIDDEN ROOTS
	if(restoreSHADOWnodes.length>0){
            for (let k in restoreSHADOWnodes) {
		if(restoreSHADOWnodes[k].original) restoreSHADOWnodes[k].node.textContent=restoreSHADOWnodes[k].original;
            }
	}

	restoreSHADOWnodes = []
        ACTIVATED=0;
    }

    function TRANSLATE_TITLE(){
      var T = document.title;
		var tk = GetHash(T,BaseGTK);                           
		var baseUrl = "https://translate.googleapis.com/translate_a/t?anno=3&client=te&v=1.0&format=html&sl="+SRL+"&tl="+TRL+"&tk="+tk;
	        var ajaxRequest = new XMLHttpRequest();
		ajaxRequest.onreadystatechange = function() {
		    if (this.readyState == 4 && this.status == 200) {
        	        var result = this.response;
			document.title = result;
        	    }
   	        }
			  

	        ajaxRequest.open("POST",baseUrl, true);
		ajaxRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	        ajaxRequest.responseType = "json";
		T = "&q="+encodeURIComponent(T);
	        ajaxRequest.send(T);

    }

    function WP_TRANSLATE_PACKAGE(){	
        if(RUNTIME_PACKAGE.length>0){
            var TEXT="";
            var realTEXT="";
	    var N = new Array()
	    TRANSLATE_TITLE();
            for (let k in RUNTIME_PACKAGE) {
		var TMP = RUNTIME_PACKAGE[k].node;
			var verify = CHECK_PACKAGE_IF_ALREADY_TRANSLATED(TMP);
			if(verify==0){
			     if(RUNTIME_PACKAGE[k].original!=""){

				TEXT = TEXT+"&q="+encodeURIComponent(RUNTIME_PACKAGE[k].original);
				realTEXT = realTEXT+RUNTIME_PACKAGE[k].original;
			        if(realTEXT.indexOf(VACINE)==-1){
					N.push (RUNTIME_PACKAGE[k].node);
				}
				k++;
			     }
			}
            }

	    RUNTIME_PACKAGE=[];
	    TEXT = TEXT.replace(/\t+/g, "");
	    TEXT = TEXT.replace(/\s+/g, ' ').trim();
	    if(TEXT!=""){
	      if(WPT_PREVIOUS != realTEXT){
       FExtension.browserInject.extensionSendMessage({greeting: 1}, function(response) {
	if(response && response.farewell){
		var theresponse = response.farewell.split("~");
		WPTdstlang=theresponse[20];

		var tmpl=theresponse[82];
		if(tmpl.indexOf(",")!=-1){
			var tmpl2 = tmpl.split(",");
			WPTdstlang = tmpl2[0];
		} else {
			WPTdstlang = tmpl;
		}
		TRL = WPTdstlang;

		SL_LOC=theresponse[22];
		SL_LNG_CUSTOM_LIST=theresponse[29];
		SL_FAV_LANGS_WPT=theresponse[82];



		var tk = GetHash(realTEXT,BaseGTK);                           
		var baseUrl = "https://translate.googleapis.com/translate_a/t?anno=3&client=te&v=1.0&format=html&sl="+SRL+"&tl="+TRL+"&tk="+tk;
	        var ajaxRequest = new XMLHttpRequest();
		ajaxRequest.onreadystatechange = function() {
		    if (this.readyState == 4 && this.status == 200) {
        	        var result = this.response;
			try{
        	            for (var i = 0; i<result.length; i++) {
				var TMP="";
				var res="";
				if(result[i].length==2) res = unescSPEC(result[i][0]);
				else res = unescSPEC(result[i]);

				res = res.replace(/i> <b/gi, "i><b");

				if(res.indexOf("<b>")!=-1){
				    var OUT = "";	
				    var SL = res.split("</i><b>");
					for(var p=0; p<SL.length; p++){
						var SL2 = SL[p].split("<i>")
						var SEG = SL2[0].replace("</b>","");
					 	OUT = OUT + SEG + " ";
					}
					res = OUT;
                                } else {
					res = res;
				}

                                res = String(res).replace(/<[^>]*>?/g,' ');
				res=res.replace(/\\/g,"");
				res=res.replace(/ ""/g,'" "');

				res= res + " ";
//                                if(N[i].node.textContent != res) TMP = N[i].node.textContent;				
//				N[i].node.textContent = res;
//				N[i].node.value=VACINE+TMP;
//				nodesTranslated.push({node: N[i].node, result: res});


                	    	if(res){	
					var TMP3="";
                         		if(N[i].node.textContent != res) TMP3 = N[i].node.textContent;
			 	 	nodesTranslated.push({node: N[i].node, result: res});
					if(TMP3!="") {
					 	N[i].node.textContent = res;
					 	N[i].node.value=TMP3;
					}
			    	}



			    }
			  N = [];
			  N.length = 0;
			} catch(ex){}			    
        	    }
   	        }
			  
		if(realTEXT!="") WPT_PREVIOUS=realTEXT;

	        ajaxRequest.open("POST",baseUrl, true);
		ajaxRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	        ajaxRequest.responseType = "json";
	        ajaxRequest.send(TEXT)
	}
      });

              }
	     }
	}
	this.focus();
    }




     function CHECK_PACKAGE_IF_ALREADY_TRANSLATED(n){
	var OUT = 0;
           for(var i=0; i<nodesTranslated.length; i++){
                if(n.textContent==nodesTranslated[i].result) {
			if(nodesTranslated.length==0) OUT=2;
			else{
				//console.log(n.textContent+"=="+nodesTranslated[i].result)
				OUT = 1; 
			}
			break;
		}
	   }
	return OUT;
     }

