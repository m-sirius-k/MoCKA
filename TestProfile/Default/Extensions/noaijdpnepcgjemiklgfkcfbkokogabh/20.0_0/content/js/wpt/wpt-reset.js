//try {
	WPT_RESTORE_ORIGINAL_NODES();
	unloadScript();
//} catch(ex){}





function unloadScript() {
    var s = document.getElementsByTagName("script");
    for(var i=0; i<s.length; i++){
	if(s[i].id == "SL_WPT"){
		document.head.removeChild(s[i]);
		//if(self != top)location.reload();

		if(self != top){
		 	var t = self.document.getElementsByTagName("script");
			for(var j=0; j<t.length; j++){
				if(t[j].id == "SL_WPT"){
					self.document.WPT_RESTORE_ORIGINAL_NODES();
					self.document.head.removeChild(t[j]);
				}
			}
		}
	}
    }    
}

