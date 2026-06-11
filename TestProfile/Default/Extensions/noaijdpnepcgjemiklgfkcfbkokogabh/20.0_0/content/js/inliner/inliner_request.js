var STOP_GOOGLE_CAPTCHA_COUNTER = 0;
var STOP_GOOGLE_CAPTCHA_LIMIT = 25;
var TMPtext="";
var DetLang="";
var GL_PR = "G";
var LOCAL_FILES = 0;
var LISTofPRpairs =    new Array ();
var LISTofLANGsetsNEW = new Array ();
var YSID="";
var AUTODET=0;
var SL_IDL="";

clearInterval(SL_IDL);

function getHttpRequest() {
    var ajaxRequest;
    try {
        ajaxRequest = new XMLHttpRequest();
    } catch (e) {
        try {
            ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
        } catch (e) {
            try {
                ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
            } catch (e) {
                alert(FExtension.element(TranslatorIM.SL_LOC,"extError1"));
                return false;
            }
        }
    }
    return ajaxRequest;
}

function truncStrByWord(str, length) {
    if (str != "undefined") {
        if (str.length > 25) {
            length = length - 25;
            var thestr = str;
            if (str.length > length) {
                str = str.substring(0, length);
                str = str.replace(new RegExp("/(.{1," + length + "})\b.*/"), "$1")    // VK - cuts str to max length without splitting words.
                var str2 = thestr.substring(length, (length + 25));
                var tempstr = str2.split(" ");
                var tmp = "";
                for (var i = 0; i < tempstr.length - 1; i++) {
                    tmp = tmp + tempstr[i] + " ";
                }
                str = str + tmp;
            }
        } else {
            str = str + " ";
        }
    }
    return str;
}






function DODetectionLang(myTransText) {
    var AUTO = SL_langSrc;
    if (TranslatorIM.SL_no_detect_it == "true") AUTO = "auto";
    if (AUTO == "auto") {
	if(STOP_GOOGLE_CAPTCHA_COUNTER<=0){
// By VK ------ removed language detection. Translation goes without the detection engine-------------
	 var a=0; // It's a fake. Remove me!!!
// By VK ------ removed language detection. Translation goes without the detection engine-------------
	}else  STOP_GOOGLE_CAPTCHA_COUNTER--;

        if (TranslatorIM.SL_TH_4 == 1 && historySentense != ""){
            historySentense = "";
        }
//		setTimeout(function() {
//        if(STOP_GOOGLE_CAPTCHA_COUNTER==0){
		        translate(myTransText, inlinerInjectDictionary);

//	} else translate(myTransText, inlinerInjectDictionary);
//		}, 0);
    } else {
        DetLang = SL_langSrc;
        if (TranslatorIM.SL_TH_4 == 1 && historySentense != ""){
            historySentense = "";
        }
        translate(myTransText, inlinerInjectDictionary);
    }
}


function injectScript(id, url, param, dictionary, text, langDst) {
 try{
	TranslatorIM.BBL_DETECT="";
	dictionary = TranslatorIM.inlinerInjectDictionary;
	LISTofPRpairs[0] = LISTofLANGsets[0];
	LISTofPRpairs[1] = LISTofLANGsets[1];
	LISTofPRpairs[2] = LISTofLANGsets[2];
	LISTofPRpairs[3] = LISTofLANGsets[3];


        langDst=TranslatorIM.SL_langDst_it;
        var langSrc=SL_langSrc;

	if(langDst == "srsl") langDst = "sr";
	if(langDst == "tlsl") langDst = "tl";
	if(TranslatorIM.SL_other_it==0) {
                TranslatorIM.SL_ALL_PROVIDERS_IT="Google";
	}

	var ACT_PR_arr = TranslatorIM.SL_ALL_PROVIDERS_IT.split(",");


        if(ACT_PR_arr[0] == "Google" && ACT_PR_arr[1] == "Microsoft" && ACT_PR_arr[2] == "Translator"){
		LISTofPRpairs[0] = LISTofPRpairs[0];
		LISTofPRpairs[1] = LISTofPRpairs[1];
		LISTofPRpairs[2] = LISTofPRpairs[3];
		LISTofLANGsetsNEW[0] = LISTofLANGsets[0];
		LISTofLANGsetsNEW[1] = LISTofLANGsets[1];
		LISTofLANGsetsNEW[2] = LISTofLANGsets[3];
	}
        if(ACT_PR_arr[0] == "Google" && ACT_PR_arr[1] == "Translator" && ACT_PR_arr[2] == "Microsoft"){
		LISTofPRpairs[0] = LISTofPRpairs[0];
		LISTofPRpairs[1] = LISTofPRpairs[3];
		LISTofPRpairs[2] = LISTofPRpairs[1];
		LISTofLANGsetsNEW[0] = LISTofLANGsets[0];
		LISTofLANGsetsNEW[1] = LISTofLANGsets[3];
		LISTofLANGsetsNEW[2] = LISTofLANGsets[1];
	}
        if(ACT_PR_arr[0] == "Microsoft" && ACT_PR_arr[1] == "Google" && ACT_PR_arr[2] == "Translator"){
		LISTofPRpairs[0] = LISTofPRpairs[1];
		LISTofPRpairs[1] = LISTofPRpairs[0];
		LISTofPRpairs[2] = LISTofPRpairs[3];
		LISTofLANGsetsNEW[0] = LISTofLANGsets[1];
		LISTofLANGsetsNEW[1] = LISTofLANGsets[0];
		LISTofLANGsetsNEW[2] = LISTofLANGsets[3];
	}
        if(ACT_PR_arr[0] == "Microsoft" && ACT_PR_arr[1] == "Translator" && ACT_PR_arr[2] == "Google"){
		LISTofPRpairs[0] = LISTofPRpairs[1];
		LISTofPRpairs[1] = LISTofPRpairs[3];
		LISTofPRpairs[2] = LISTofPRpairs[0];
		LISTofLANGsetsNEW[0] = LISTofLANGsets[1];
		LISTofLANGsetsNEW[1] = LISTofLANGsets[3];
		LISTofLANGsetsNEW[2] = LISTofLANGsets[0];
	}
        if(ACT_PR_arr[0] == "Translator" && ACT_PR_arr[1] == "Google" && ACT_PR_arr[2] == "Microsoft"){
		LISTofPRpairs[0] = LISTofPRpairs[3];
		LISTofPRpairs[1] = LISTofPRpairs[0];
		LISTofPRpairs[2] = LISTofPRpairs[1];
		LISTofLANGsetsNEW[0] = LISTofLANGsets[3];
		LISTofLANGsetsNEW[1] = LISTofLANGsets[0];
		LISTofLANGsetsNEW[2] = LISTofLANGsets[1];
	}
        if(ACT_PR_arr[0] == "Translator" && ACT_PR_arr[1] == "Microsoft" && ACT_PR_arr[2] == "Google"){
		LISTofPRpairs[0] = LISTofPRpairs[3];
		LISTofPRpairs[1] = LISTofPRpairs[1];
		LISTofPRpairs[2] = LISTofPRpairs[0];
		LISTofLANGsetsNEW[0] = LISTofLANGsets[3];
		LISTofLANGsetsNEW[1] = LISTofLANGsets[1];
		LISTofLANGsetsNEW[2] = LISTofLANGsets[0];
	}

        if(ACT_PR_arr[0] == "Google"){
		LISTofPRpairs[0] = LISTofPRpairs[0];
		LISTofLANGsetsNEW[0] = LISTofLANGsets[0];
	}

        var ACT_PR = ACT_PR_arr[0];

	var ListProviders = "";
        for(var I=0; I<LISTofPRpairs.length; I++){
	        if(TranslatorIM.FIND_PROVIDER(LISTofPRpairs[I],langDst)!=-1 ){
			ListProviders=ListProviders+ACT_PR_arr[I]+",";
		}
	}

	if(ListProviders!=""){
	 	var arr = ListProviders.split(",");
		ACT_PR = arr[0];
	}




	if(TranslatorIM.IT_SRC=="auto" || TranslatorIM.SL_no_detect_it=="true") AUTODET=1;
	if(TranslatorIM.INLINEflip==1) AUTODET=1;



        var result="";
	var theQ = text.split(" ");
        if(text.match(/[-/‧·﹕﹗！：，。﹖？:-?!.,:{-~!"^_`、\[\]]/g)!=null) theQ=100;
  	if(text.match(/[\u3400-\u9FBF]/) && text.length>1) theQ=100;
	var st = IF_TO_AVAILABLE_IN_GOOGLE(LISTofPRpairs, langDst);
	if(dictionary==true){
//		if(theQ.length==1 && st!=0) ACT_PR = "Google";        
		if(theQ.length==1) ACT_PR = "Google";        
	}

        var big5 = DetectBig5(text);
        var TMO=20;
        if(AUTODET==1){
		if(big5==0) INLINE_DETECT(text);
		else MS_DETECTOR(text);
/*
		if(ACT_PR == "Google") TMO=300;
		if(ACT_PR == "Microsoft") TMO=300;
		if(ACT_PR == "Translator") TMO=300;
*/
	}


        setTimeout(function(){
            var cntr=0
	    var SL_IDL = setInterval(function(){
		if(cntr>50) clearInterval(SL_IDL);
		else {
		  if(TranslatorIM.BBL_DETECT!="") {
			clearInterval(SL_IDL);
        		var marker=0;
	       		if(ACT_PR == "Microsoft") marker=1;
	        	if(ACT_PR == "Translator") marker=3;

			if((TranslatorIM.BBL_DETECT=="" || TranslatorIM.BBL_DETECT=="<#>") && AUTODET==0)TranslatorIM.BBL_DETECT=TranslatorIM.IT_SRC;
			var FAP = FIRST_AVAILABLE_PROVIDER(ACT_PR,marker,LISTofLANGsetsNEW,TranslatorIM.BBL_DETECT,langDst);
			if(FAP != ""){
				ACT_PR = FAP;
		        	marker=0;
		        	if(ACT_PR == "Google") GL_PR = "G";
        			if(ACT_PR == "Microsoft") {marker=1; GL_PR = "M";}
			        if(ACT_PR == "Translator") {marker=3; GL_PR = "T";}

				ACT_PR = LOCAL_FILES_HANDLER(ACT_PR);

				if(ACT_PR=="Translator"){
				        var marker=0;
				        var marker2=0;
				   	var arr = LISTofPRpairs[2].split(",");
					for(var j=0; j<arr.length; j++){
						if(arr[j] == TranslatorIM.BBL_DETECT) marker++;
					}	
					if(marker==0){
						ACT_PR="Microsoft";
					}
	//				if(TranslatorIM.BBL_DETECT == langDst) ACT_PR="Google";

				}


				if(ACT_PR=="Google"){
					if(TranslatorIM.IT_SRC=="auto" || TranslatorIM.SL_no_detect_it=="true") AUTODET=1;
				//	if(TranslatorIM.INLINEflip==1) AUTODET=1;
					var dir=TranslatorIM.IT_SRC+"-"+TranslatorIM.IT_DST;
					if(AUTODET==1 && dir.indexOf("auto")!=-1){
					dir=DetLang+"_"+TranslatorIM.IT_SRC;
					if(dir.indexOf("auto")!=-1) dir=DetLang+"-"+TranslatorIM.IT_DST;
					} else {
						if(TranslatorIM.INLINEflip==0){
        						if(TranslatorIM.SL_no_detect_it=="true") dir=DetLang+"-"+TranslatorIM.IT_DST;
						}
					}

					dir = dir.replace("zh-TW","zt");
					dir = dir.replace("zh-CN","zh");
				  	FExtension.browserInject.runtimeSendMessage({greeting: "IT:>" + id+ ":|:"+ url+ ":|:"+ param+ ":|:"+ dictionary+ ":|:"+ text+ ":|:"+ dir+ ":|:"+ window.location+ ":|:"+ DetLang}, function(response) {}); 
				} 
				if(ACT_PR=="Microsoft"){
				    setTimeout(function() {
					var ln = langDst;
					DetLang = TranslatorIM.BBL_DETECT;
				
				        if(TranslatorIM.INLINEflip==1){
						if(DetLang.indexOf("#")!=-1){
							DetLang = TranslatorIM.IT_DST;
							TranslatorIM.BBL_DETECT = DetLang;
							if(langSrc=="auto"){
								DetLang = "en";
								TranslatorIM.BBL_DETECT = "en";
							}
						}
					}


				        if(TranslatorIM.INLINEflip==1){					
						if(DetLang==ln){
							if(TranslatorIM.IT_SRC != "auto"){
								ln = TranslatorIM.IT_SRC;
							}
						}

						if(DetLang.indexOf("#")==-1){
							TranslatorIM.BBL_DETECT = TranslatorIM.IT_DST;						
						} else TranslatorIM.BBL_DETECT = langDst;

						//DetLang = "en";
					}


			     		if(LISTofLANGsets[marker].indexOf(ln)==-1) {
						MS(id, url, param, dictionary, text, ln, window.location, GL_PR, 0);
				        }else{
						MS(id, url, param, dictionary, text, ln, window.location, GL_PR, 1);
					}
				    }, 150);
				}
		
				if(ACT_PR=="Translator"){
					   if(IF_DIR_AVAILABLE(LISTofPRpairs,DetLang,langDst)!=0){
						YAND(id, url, param, dictionary, text, langDst, window.location, GL_PR);
					   } else {
						result=TranslatorIM.SL_GetLongName(langDst)+": " + FExtension.element(TranslatorIM.SL_LOC,"extnotsupported");
					        translateCallBack(result, false, text);
					   }	
				} 
			} else {
			   if(TranslatorIM.BBL_DETECT!="<#>"){
				var result=FExtension.element(TranslatorIM.SL_LOC,"extLPNotSupported");
				result=result.replace("XXX",TranslatorIM.SL_GetLongName(TranslatorIM.BBL_DETECT))
				result=result.replace("YYY",TranslatorIM.SL_GetLongName(langDst));
			        translateCallBack(result, false, text);
			   } else {
				if(result==""){
					var result=FExtension.element(TranslatorIM.SL_LOC,"extnotrsrv");
				        translateCallBack(result, false, text);
				}
	                   }

			}

			  }
		  }
		cntr++;
	    },20);  

     },TMO); //WAS:600
 } catch (e){chrome.runtime.lastError}	
}

function INLINE_DETECT(text){
	GOOGLE_DETECTOR(text);
	//MS_DETECTOR(text);
}


function MS_DETECTOR(text){
	var TM = 10;
	setTimeout(function(){
	    if(TranslatorIM.AKEY!=""){
	        var baseUrl = "https://api-edge.cognitive.microsofttranslator.com/translate?api-version=3.0&includeSentenceLength=false&to=en";
		var ajaxRequest;  
		try{
			ajaxRequest = new XMLHttpRequest();
		} catch (e){
			try{
				ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
			} catch (e) {
				try{
					ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
				} catch (e){
					SL_alert(FExtension.element(FExtension.GET_localStorage("SL_LOCALIZATION"),'extError1'));
					return false;
				}
			}
		}
		ajaxRequest.onreadystatechange = function(){
			if(ajaxRequest.readyState == 4){
		             	var resp = ajaxRequest.responseText;
			        if(resp.indexOf('{"error":{"code"')==-1){
			             	var R1=resp.split('language":"');
					var R2=R1[1].split('","score"');
					DetLang = R2[0];
					if(DetLang == "zh-Hans") DetLang = "zh-CN";
					if(DetLang == "zh-Hant") DetLang = "zh-TW";
					if(DetLang == "he") DetLang = "iw";
				        if(DetLang == "sr-Cyrl") DetLang = "srsl";
					if(DetLang == "fil") DetLang = "tl";
					if(DetLang == "mww") DetLang = "hmn";
					if(DetLang == "ku") DetLang = "ckb"; 
					TranslatorIM.BBL_DETECT = DetLang;
					if(DetLang!="") {
						var ln;
						if(TranslatorIM.INLINEflip==1){				
							if(DetLang==TranslatorIM.SL_langDst_it && SL_langSrc!="auto") ln = SL_langSrc;
							else ln = TranslatorIM.SL_langDst_it;
						} else ln = TranslatorIM.SL_langDst_it;
					}

				}// else GOOGLE_DETECTOR(text);

			}
		}

		text=text.replace(/"/g,"'");
		ajaxRequest.open("POST", baseUrl, true);
		ajaxRequest.setRequestHeader("Content-Type", "application/json");
		ajaxRequest.setRequestHeader("authorization",TranslatorIM.AKEY);
		ajaxRequest.send('[{"text":"'+text+'"}]'); 
          }
	},TM);
}


function GOOGLE_DETECTOR(text){
		    var text_ = truncStrByWord(text,100);
		    var num = Math.floor((Math.random() * SL_GEO.length)); 
		    var theRegion = SL_GEO[num];
		    var baseUrl ="https://translate.google."+theRegion+"/translate_a/single";
		    var SL_Params = "client=gtx&dt=t&dt=bd&dj=1&source=input&q="+encodeURIComponent(text_)+"&sl=auto&tl=en&hl=en";

			   chrome.runtime.sendMessage({from:"content_detect", url: baseUrl, cgi:SL_Params,});
			   chrome.runtime.onMessage.addListener(function(msg) {
				   if (msg.from == "background") {
					TranslatorIM.BBL_DETECT = msg.detected;
					if(TranslatorIM.BBL_DETECT!="" && TranslatorIM.BBL_DETECT!="<#>") {
						var resp = TranslatorIM.BBL_DETECT;
						DetLang = TranslatorIM.BBL_DETECT;
					        if(resp!="") {
					                var ln;
							if(TranslatorIM.INLINEflip==1){
								if(DetLang==TranslatorIM.SL_langDst_it && SL_langSrc!="auto") ln = SL_langSrc;
								else ln = TranslatorIM.SL_langDst_it;
							} else ln = TranslatorIM.SL_langDst_it;
						}

					} else MS_DETECTOR(text_);

				   }	
			   });
}

function FIRST_AVAILABLE_PROVIDER(ACT_PR,marker,langs,from,to){
	//if(from=="") from="en";
	var CUR_P_LIST = TranslatorIM.SL_ALL_PROVIDERS_IT.split(",");
	var out="";
	var cnt = 0;
	var arr = langs[0].split(",");
	for(var i=0; i<arr.length; i++){        
		if(arr[i]==to) cnt++;
		if(arr[i]==from) cnt++;
	}
	if(cnt<2){
		for(var i=0; i<langs.length; i++){
	   		var arr = langs[i].split(",");
			var cnt1=0;
			var cnt2=0;
			for(var j=0; j<arr.length; j++){
				if(arr[j] == from) cnt1++;
				if(arr[j] == to) cnt2++;
			}	
			if(cnt1>0 && cnt2 > 0 && i==0) out=CUR_P_LIST[0]+",";
			if(cnt1>0 && cnt2 > 0 && i==1) out=out+CUR_P_LIST[1]+",";
			if(cnt1>0 && cnt2 > 0 && i==2) out=out+CUR_P_LIST[2]+",";
		}
		if(out!=""){
		 	var tmp = out.split(",");
			out = tmp[0];
		}
	} else out = ACT_PR;
	return(out);
}

function IF_TO_AVAILABLE_IN_GOOGLE(langs, to){
	var cnt=0;
   	var arr = langs[0].split(",");
	for(var j=0; j<arr.length; j++){
		if(arr[j] == to) cnt++;
	}	
	return(cnt);
}

function IF_DIR_AVAILABLE(langs, from, to){
	var cnt=0;
	for(var i=0; i<langs.length; i++){
	   	var arr = langs[i].split(",");
		var cnt1=0;
		var cnt2=0;
		for(var j=0; j<arr.length; j++){
			if(arr[j] == from) cnt1++;
			if(arr[j] == to) cnt2++;
		}	
		if(cnt1>0 && cnt2 > 0) cnt++
	}
	return(cnt);
}



            
function MS(id, url, param, dictionary, text, ln, wnd, GL_PR, key){

	        if(ln == "zh") ln = "zh-CHS";
       		if(ln == "zt") ln = "zh-CHT";
	        if(ln == "iw") ln = "he";
       		if(ln == "sr") ln = "sr-Cyrl";
	        if(ln == "tl") ln = "fil";
       		if(ln == "hmn") ln = "mww";
	        if(ln == "ku") ln = "kmr";
       		if(ln == "ckb") ln = "ku";
	        if(ln == "srsl") ln = "sr";
       		if(ln == "tlsl") ln = "fil";

		var TM = 0;
		setTimeout(function(){
		    if(TranslatorIM.AKEY!=""){
		        var baseUrl = "https://api-edge.cognitive.microsofttranslator.com/translate?api-version=3.0&includeSentenceLength=false&to="+ln;

			var ajaxRequest;  
			try{
				ajaxRequest = new XMLHttpRequest();
			} catch (e){
				try{
					ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
				} catch (e) {
					try{
						ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
					} catch (e){
						SL_alert(FExtension.element(FExtension.GET_localStorage("SL_LOCALIZATION"),'extError1'));
						return false;
					}
				}
			}
			ajaxRequest.onreadystatechange = function(){
				if(ajaxRequest.readyState == 4){ 
		        	     	var resp = ajaxRequest.responseText;
					if(resp.indexOf('{"error":{"code"')==-1){
						var R1 = resp.split('"translations":[{"text":"');
						var R2 = R1[1].split('",');
						var RESULT = R2[0];
						RESULT = JSON.parse(`"${RESULT}"`);
					    	dictionary=false;
					    	if(RESULT=="") RESULT=FExtension.element(TranslatorIM.SL_LOC,"extnotrsrv");
//	    					RESULT = RESULT.replace(/\\"/g,"'");
//	                                        RESULT = RESULT.replace(/\\"/g,'"');
					        RESULT = RESULT.replace(/\\u00A0/g,'');
	    					translateCallBack(RESULT, dictionary, text);
					}else SL_TR_ROUTER(id, url, param, dictionary, text, ln, wnd, GL_PR);
				}
			}
		        var OUT="";
		        if(OUT=="") OUT=text;
			OUT=OUT.replace(/"/g,"'");
			ajaxRequest.open("POST", baseUrl, true);
			ajaxRequest.setRequestHeader("Content-Type", "application/json");
			ajaxRequest.setRequestHeader("authorization", TranslatorIM.AKEY);
			ajaxRequest.send('[{"text":"'+OUT+'"}]'); 
		  }else SL_TR_ROUTER(id, url, param, dictionary, text, ln, wnd, GL_PR);
		},TM);		

	
}




function translate(text, injectDictionary) {

    var escapedText = text.replace(/#/g, "");
//    escapedText = escapedText.replace(/%/g, "");
    var langSrc = "auto";
    var SL_TMPTMP1=FExtension.element(TranslatorIM.SL_LOC,'extLanguages').split(",")
//    var SL_TMPTMP1=ImTranslatorBG.SL_ListOfAvailableLanguages.split(",");
    for (var i = 0; i < SL_TMPTMP1.length; i++) {
        var SL_TMPTMP2 = SL_TMPTMP1[i].split(":");
        if (SL_TMPTMP2[0] == DetLang) {
//            langSrc = DetLang;
            break;
        }
    }


    var langDst = SL_langDst;

// By VK ------ Translation goes without the detection engine-------------

    if(langSrc != "auto" && DetLang == langDst){
      langDst = langSrc;
      langSrc = SL_langSrc;
      if(langSrc!="auto"){
	      var tmp = langSrc;
	      langSrc = langDst;
	      langDst = tmp;
      }
    }

// By VK ------ Translation goes without the detection engine-------------

    var baseUrl = "";
    var SL_Params = "";
    var array = text.match(/\b\w+\b/g);

    var arraySplit = text.split(' ');
    //var dictionary = false;
    var a=Math.floor((new Date).getTime()/36E5)^123456;
    var tk = a+"|"+Math.floor((Math.sqrt(5)-1)/2*(a^654321)%1*1048576);


    if (injectDictionary && dictionary){//array && array.length == 1 && arraySplit && arraySplit.length == 1) {
        //escapedText = escapedText.replace(/[\.,-\/#!$%\^&\*;:{}=\-_`~()]/g,"");

	var num = Math.floor((Math.random() * SL_GEO.length)); 
	var theRegion = SL_GEO[num];

        if(TranslatorIM.SL_DOM!="auto") theRegion=TranslatorIM.SL_DOM;

        //INLINE DICTIONARY REQUEST
	baseUrl = "https://translate.google."+theRegion+"/translate_a/single";
	SL_Params = "client=gtx&dt=t&dt=bd&dj=1&source=input&q=" + encodeURIComponent(dictionaryWord.toLowerCase()) + "&sl=auto&tl=" + langDst + "&hl=en";

        //dictionary = true;
    } else {
	var num = Math.floor((Math.random() * SL_GEO.length)); 
	var theRegion = SL_GEO[num];
        if(TranslatorIM.SL_DOM!="auto") theRegion=TranslatorIM.SL_DOM;
	baseUrl = "https://translate.google."+theRegion+"/translate_a/single";
	SL_Params = "client=gtx&dt=t&dt=bd&dj=1&source=input&q=" + encodeURIComponent(escapedText) + "&sl=auto&tl=" + langDst + "&hl=en";
    }

    injectScript("inlinerScript", baseUrl, SL_Params, dictionary, text, langDst);

}


function translateCallBack(result, dictionary, text) {
    var translation = "";
    //if(result.indexOf('TRANSLATED_TEXT')!=-1){


    if (dictionary) {
        try {
            result = JSON.parse(result);
        } catch (e) {

        }

        if (result.dict) {
            var dict = result.dict;
            if (dict.length > 0 && dict[0].terms) {
                translation = dict[0].terms.join(', ');
            }
        } else {
            translation = result.sentences[0].trans;
        }
    } else {
        translation = get_translation(result);
    }
    //}


	if(TranslatorIM.IT_SRC=="auto" || TranslatorIM.SL_no_detect_it=="true") AUTODET=1;
//	if(TranslatorIM.INLINEflip==1) AUTODET=1;
	var dir=TranslatorIM.IT_SRC+"_"+TranslatorIM.IT_DST;
	if(AUTODET==1 && dir.indexOf("auto")!=-1){
		dir=DetLang+"_"+TranslatorIM.IT_SRC;
		if(dir.indexOf("auto")!=-1) dir=DetLang+"_"+TranslatorIM.IT_DST;
	} else {
		if(TranslatorIM.INLINEflip==0){
        		if(TranslatorIM.SL_no_detect_it=="true") dir=DetLang+"_"+TranslatorIM.IT_DST;
		}
	}


    SaveTransToHistory(text,translation,dir);
    translation = " " + translation;
    inlinerInjectHandleMessage({name: "inlinerSelectionResponse", message: translation});

}

function get_translation(result){
 result = result.replace(/\\"/ig, '"');
 if(result.indexOf('<span id')!=-1){
    if (result.indexOf('<span id=result_box class="long_text">') > -1)   var ImtranslatorGoogleResult1 = result.split('<span id=result_box class="long_text">');
    else var ImtranslatorGoogleResult1 = result.split('<span id=result_box class="short_text">');
    var ImtranslatorGoogleResult2 = ImtranslatorGoogleResult1[1].split('</span></div>');
    var ImtranslatorGoogleResult3 = ImtranslatorGoogleResult2[0].replace(/<br>/ig, '@');
    ImtranslatorGoogleResult3 = ImtranslatorGoogleResult3.replace(/&#39;/ig, "'");
    ImtranslatorGoogleResult3 = ImtranslatorGoogleResult3.replace(/&quot;/ig, "'");
    ImtranslatorGoogleResult3 = ImtranslatorGoogleResult3.replace(/&amp;/ig, "&");
    ImtranslatorGoogleResult3 = ImtranslatorGoogleResult3.replace(/(<([^>]+)>)/ig, "");
    ImtranslatorGoogleResult3 = ImtranslatorGoogleResult3.replace(/@/ig, "<br>");
    var ImtranslatorGoogleResult4 = ImtranslatorGoogleResult3.replace(/% 20/ig, " ");
//    ImtranslatorGoogleResult4 = ImtranslatorGoogleResult4.charAt(0).toUpperCase() + ImtranslatorGoogleResult4.slice(1);
    return ImtranslatorGoogleResult4;
 } else return result;
}


function SaveTransToHistory(text,historyText, dir) {
        if (TranslatorIM.SL_TH_4 == 1){

	    var mySourceLang = TranslatorIM.IT_SRC;
    	    var myTargetLang = TranslatorIM.IT_DST;


	    if(TranslatorIM.IT_SRC!="auto" && TranslatorIM.SL_no_detect_it!="true"){
		DetLang=TranslatorIM.IT_SRC;
	    } 


	    if(TranslatorIM.INLINEflip==0){
		if(DetLang!="") mySourceLang = DetLang;
		else mySourceLang = "auto";
	    } else {
		    if(DetLang==myTargetLang && mySourceLang!="auto"){
			var tmp = myTargetLang;
			myTargetLang = mySourceLang;
			mySourceLang = tmp;
		    }else mySourceLang = DetLang;
	    } 

            var SLnow = new Date();
            SLnow = SLnow.toString();
            var TMPtime = SLnow.split(" ");
            var CurDT = TMPtime[1] + " " + TMPtime[2] + " " + TMPtime[3] + ", " + TMPtime[4];
            text=text.replace(/~/ig," ");
            historyText=historyText.replace(/~/ig," ");

            FExtension.browserInject.runtimeSendMessage({greeting: "[i]" + text + "~~" + historyText + "~~" + mySourceLang + "|" + myTargetLang + "~~" + FExtension.browserInject.getDocument().location + "~~" + CurDT + "~~5~~"+GL_PR+"^^"}, function (response) {
                if(response){
                    //console.log(response.farewell);
                }
            });
         }
 DetLang="";
}


function LOCAL_FILES_HANDLER(ACT_PR){
	//VK ; local files
	var WL = String(window.location).toLowerCase();
	var out=ACT_PR;
	if(WL.indexOf("file:///")!=-1 && (WL.indexOf(".html")>-1 || WL.indexOf(".htm")>-1 || WL.indexOf(".txt")>-1)) {
		LOCAL_FILES=1;
		out="Microsoft";
	}
	return(out);
	//------------
}

function DetectBig5(myTransText){
	var all = myTransText.length;
	var count = 0;
	for (var i = 0, len = myTransText.length; i < len; i++) {
		var rr = myTransText[i].match(/[\u3400-\u9FBF]/);
		if(rr) count ++;
	}
	var other = all-count;
	var OUT = 0	
	if(other<=count) OUT=1
	return(OUT);
}


function YAND(id, url, param, dictionary, text, langDst, winloc, GL_PR){
	if(TranslatorIM.IT_SRC=="auto" || TranslatorIM.SL_no_detect_it=="true") AUTODET=1;
//	if(TranslatorIM.INLINEflip==1) AUTODET=1;
	var dir=TranslatorIM.IT_SRC+"-"+TranslatorIM.IT_DST;
	if(AUTODET==1 && dir.indexOf("auto")!=-1){
		dir=DetLang+"-"+TranslatorIM.IT_SRC;
		if(dir.indexOf("auto")!=-1) dir=DetLang+"-"+TranslatorIM.IT_DST;
	} else {
		if(TranslatorIM.INLINEflip==0){
        		if(TranslatorIM.SL_no_detect_it=="true") dir=DetLang+"-"+TranslatorIM.IT_DST;
		}//else 	dir=DetLang+"-"+TranslatorIM.IT_DST;
	}

	FExtension.browserInject.runtimeSendMessage({greeting: "ITY:>" + id+ ":|:"+ url+ ":|:"+ param+ ":|:"+ dictionary+ ":|:"+ text+ ":|:"+dir+ ":|:"+ winloc+ ":|:"+ GL_PR+ ":|:"+ DetLang}, function(response) {}); 
}

function SL_TR_ROUTER(id, url, param, dictionary, text, ln, wnd, GL_PR){
   if(IF_DIR_AVAILABLE(LISTofPRpairs,DetLang,ln)!=0){
	YAND(id, url, param, dictionary, text, ln, wnd, GL_PR);
   } else {
	var result=TranslatorIM.SL_GetLongName(ln)+": " + FExtension.element(TranslatorIM.SL_LOC,"extnotsupported");
        translateCallBack(result, false, text);
   }	
}


