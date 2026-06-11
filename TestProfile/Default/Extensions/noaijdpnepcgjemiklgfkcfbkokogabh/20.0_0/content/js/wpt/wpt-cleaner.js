try{
 var isScrolling ;
 HideAllMoBoxes();
 unloadScript();
 CleanUpAllIframes();
 if(isScrolling) clearInterval(isScrolling);
 disableMutatinObserver();
 WPT_RESTORE_ORIGINAL_NODES();
 RESTORE=1;
}catch(ex){}

function CleanUpAllIframes(){
    try{
	var iframes = document.querySelectorAll('iframe');
	for (var i = 0; i < iframes.length; i++) {
		iframes[i].contentWindow.focus();
		iframes[i].contentWindow.WPT_RESTORE_ORIGINAL_NODES();		

	}
    }catch(ex){}	
}

function unloadScript() {
    var s = document.getElementsByTagName("script");
    for(var i=0; i<s.length; i++){
	if(s[i].id == "SL_WPT"){
		document.head.removeChild(s[i]);
//		if(self != top) location.reload();
	}
    }    
}

function HideAllMoBoxes() {
    var s = document.getElementsByTagName("div");
    for(var i=0; i<s.length; i++){
	if(s[i].id == "move"){
		s[i].style.display="none";
	}
    }    
}


