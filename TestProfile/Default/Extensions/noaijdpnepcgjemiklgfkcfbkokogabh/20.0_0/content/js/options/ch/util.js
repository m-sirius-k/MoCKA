function SL_LANGS(){
		if(GEBI('autohotkeys')){
		  var frame = GEBI('autohotkeys');
		  if(frame)	frame.parentNode.removeChild(frame);
		}
		const isMacBrowser = /Mac|iPod|iPhone|iPad/.test(navigator.platform);
		var H = "1490px";
		var LOC = GET("SL_LOCALIZATION");
		if(LOC=="zh" || LOC=="zt" || LOC=="ko") H = "1520px";
		if(LOC=="ja") H = "1700px";
		if(LOC=="hi") H = "1530px";
		if(isMacBrowser==true){
			var LOC = GET("SL_LOCALIZATION");
			if(LOC=="zh" || LOC=="zt" || LOC=="ko" || LOC=="ja") H = "1550px";
		}

		if(!GEBI("autohotkeys")){
		    var die = document.createElement("iframe");
		    die.src = "languages.html";
		    die.name = "autohotkeys";
		    die.id="autohotkeys";
		    die.width="750px";
		    die.height=H;
		    die.scrolling="no";
                    die.background="#eee";
		    die.frameBorder="0";
		    GEBI('SL_AUTOKEYS').style.display='block';
		    GEBI('SL_AUTOKEYS').style.width='750px';
		    GEBI('SL_AUTOKEYS').style.height=H;
		    GEBI('SL_AUTOKEYS').appendChild(die);
		}
}
function CUSTOM_LANGS(list){
        list = list.replace(/&#160;/ig," ");
        var list2 = GET("SL_LNG_LIST");
	if(list2=="all") return LANGS_FILTER(list);
	else{
	    var OUT = "";
	    var L1 = list.split(",");
	    for(var i=0; i<L1.length; i++){
	     	var L1base = L1[i].split(":");
	     	var L1short = list2.split(",");
		for(var j=0; j<L1short.length; j++){
		   if(L1base[0] == L1short[j]) OUT=OUT+L1short[j]+":"+L1base[1]+",";
		}
	    }
 	    OUT = OUT.substring(0,OUT.length-1);
	    OUT=LANGS_FILTER(OUT)
	    return OUT;
	}
}

function CUSTOM_LANGS_RESET_TO_DEFAULT(list){
	var OUT = "";
        list = list.replace(/&#160;/ig," ");
        list = list.replace(/all,/ig,"all");
        list = list.split(",");
	var list2 = FExtension.element(GET("SL_LOCALIZATION"),'extLanguages');

	if(list!="all"){

	    	var L1 = list2.split(",");
		for(var i=0; i<L1.length; i++){
	     		var L2 = L1[i].split(":");
			for(var j=0; j<list.length; j++){		
			   if(L2[0] == list[j]) OUT=OUT+list[j]+":"+L2[1]+",";
			}
		    }
 		    OUT = OUT.substring(0,OUT.length-1);
		    OUT=LANGS_FILTER(OUT);
	} else  OUT = LANGS_FILTER(list2);
        return OUT;
}


function CUSTOM_LANGS_RESET_TO_DEFAULT__(list){
        list = list.replace(/&#160;/ig," ");
	var list2 = LISTofPRpairsDefault;
	if(list2=="all") return LANGS_FILTER(list);
	else{
	    var OUT = "";
	    var L1 = list.split(",");
	    for(var i=0; i<L1.length; i++){
	     	var L1base = L1[i].split(":");
	     	var L1short = list2.split(",");
		for(var j=0; j<L1short.length; j++){
		   if(L1base[0] == L1short[j]) OUT=OUT+L1short[j]+":"+L1base[1]+",";
		}
	    }
 	    OUT = OUT.substring(0,OUT.length-1);
	    OUT=LANGS_FILTER(OUT)

	    return OUT;
	}
}

function LANGS_FILTER(SL_Languages){
        var OUT="";
	var GLOBAL_LANG_LIST=LISTofPRpairsDefault.split(",");
	var ARR = SL_Languages.split(",");
	var cnt=0;
	for(var i=0; i<ARR.length; i++){
	 	var NAME=ARR[i].split(":");
		for(var j=0; j<GLOBAL_LANG_LIST.length; j++){
			if(NAME[0]==GLOBAL_LANG_LIST[j]) OUT = OUT + NAME[0] + ":" + NAME[1] + ","
		}
	}
	OUT = OUT.substring(0,OUT.length-1);		    
	return(OUT)
}


function RESET_TEMPS_TO_DEFAULT(){
	   	   //Reset BBL temps
		   SET("BL_D_PROV", "");
		   SET("BL_T_PROV", "");
		   SET("SL_BBL_X", 0);
		   SET("SL_BBL_Y", 0);
	   	   SET("SL_langSrc_bbl2",GET("SL_langSrc_bbl"));
	   	   SET("SL_langDst_bbl2",GET("SL_langDst_bbl"));
	   	   SET("SL_Fontsize_bbl2",GET("SL_Fontsize_bbl"));

	   	   SET("SL_pin_bbl2",GET("SL_pin_bbl"));
	   	   SET("SL_show_button_bbl2",GET("SL_show_button_bbl"));
	   	   if(GET("SL_no_detect_bbl")=="true")   SET("SL_bbl_loc_langs","false");
	   	   else    SET("SL_bbl_loc_langs","true");

	  	   //Reset IT temps
	   	   SET("SL_langDst_it2",GET("SL_langDst_it"));
}
