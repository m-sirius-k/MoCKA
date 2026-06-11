var STR = "";
var TRANSLATOR;
var TXT;

setTimeout(function() {	
	TRANSLATOR = GET("SL_PrefTrans");
	TXT = GET("SL_Dtext");
	var STOP = 0;

	 switch(TRANSLATOR){
	   case "1":	
        	StartImTranslator();
		break;
	   case "2":
		chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
		    var my_tabid=tabs[0].id;
		    var STR1 = String(document.location);
   		    if(STR1.indexOf("text=")!=-1){
			var STR2 = STR1.split("text=");
			STR = STR2[1];
		    }else	STR = TXT;
		    if(STR!=""){
			chrome.tabs.sendMessage(my_tabid, {action: 'open_inline'});  
                        window.close();
		    } else {
			document.write("<div style='width:140px;'><div align=center>"+FExtension.element(GET("SL_LOCALIZATION"),"extpst").replace(/ /ig,"&nbsp;")+"</div></div>");
		    }
		}); 
		break;

	   case "3":
		chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
		    var my_tabid=tabs[0].id;
		    var STR1 = String(document.location);
   		    if(STR1.indexOf("text=")!=-1){
			var STR2 = STR1.split("text=");
			STR = STR2[1];
		    }else	STR = TXT;
		    if(STR!=""){
			chrome.tabs.sendMessage(my_tabid, {action: 'open_bubble'});  
                        window.close();
		    } else {
			document.write("<div style='width:140px;'><div align=center>"+FExtension.element(GET("SL_LOCALIZATION"),"extpst").replace(/ /ig,"&nbsp;")+"</div></div>");
		    }
		}); 
		break;
	   case "4":
		chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
		        var my_tabid=tabs[0].id;
			chrome.tabs.sendMessage(my_tabid, {action: 'open_wpt'});  
                        window.close();
		}); 
		break;

	   case "5":
		chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
		        var my_tabid=tabs[0].id;
			chrome.tabs.sendMessage(my_tabid, {action: 'open_mo'});  
                        window.close();
		}); 
		break;
	 }	
}, TIME_OUT);

function StartImTranslator(){
	var BACK_VIEW=GET("SL_BACK_VIEW");
	var STR1 = String(document.location);
	if(STR1.indexOf("text=")!=-1){
		var STR2 = STR1.split("text=");
		STR = "?text="+STR2[1];
	}else	STR = "?text="+TXT;
//	STR = STR + "&stop=";	
	if(STR1.indexOf("&stop=")!=-1){
//		STR = STR + "&stop=";
		STOP = 1;
	}

       	if(window.location.pathname.indexOf("router.html")!=-1){
		if(BACK_VIEW==2) document.location="TB-translation-back.html" + STR; 
//		else		 document.location="TB-translator.html" + STR + "&tb="; 
		else		 document.location="TB-translator.html" + STR; 
	}else{
		if(STOP == 0){
			if(BACK_VIEW==1) document.location="TB-translator.html" + STR;
			else 		 document.location="TB-translation-back.html" + STR; 
		}
	}
}
