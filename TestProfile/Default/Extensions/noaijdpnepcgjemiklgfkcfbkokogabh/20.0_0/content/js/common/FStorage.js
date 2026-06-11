try{
FExtension.store = {
    SL_BR_LN: "en",
    SL_PR_ALL: "Google,Microsoft,Translator,Yandex",
    SL_PR_KEYS: "Google:1,Microsoft:0,Translator:0,Yandex:0",
    SL_PR_IT: "Google,Microsoft,Yandex",
    profile_Folder: "ImTranslator",
    cl_Profile_Name: "profile.imt",
    global_pref_data: {},
    domStorageManager: null,
    domStorageUri: null,
    ioService: null,
    scriptSecManager: null,
    scriptSecPrincipal: null,
    localStorage: (FExtension.browser.isLocalStoragePreset()) ? localStorage : null,
    cachedSbDomainName: (FExtension.browser.isLocalStoragePreset()) ? "imtranslator.net" : null,
    initialized: FExtension.browser.isLocalStoragePreset(),
    getLocalStorage: function() {
        if (FExtension.browser.isLocalStoragePreset() || FExtension.store.initialized){
            return FExtension.store.localStorage;
	}	
    },

    SL_CUR_LANG: function(){
		var BRloc=chrome.i18n.getUILanguage().substr(0,2);
		if(BRloc!=""){
		   var BRlanguage="en"
		   var Arr = LISTofPRpairsDefault.split(",")
		   for(var I=0; I<Arr.length; I++){
	        	var lng = Arr[I].replace("zh-TW","zh");
		        lng = lng.replace("zh-CN","zh");
		   	if(BRloc==lng){
			  BRlanguage=lng;
			  break;
			}
		   }
		}
	 return(BRlanguage);	
    },


    loadNewParams : function(){
        FExtension.store.setDefault();
    },

    set : function(key, value){              // Storing key function
        var obj = false;
        if (typeof(value) == 'object'){
            value = JSON.stringify(value);
            obj = true;
        }
        FExtension.store.getLocalStorage().setItem(key, obj ? 'obj_'+value : value+'');
    },
    get : function(key){                  // Retrieving key function
        var val = null;
        val = FExtension.store.getLocalStorage().getItem(key);

        if (val && val.indexOf('obj_') == 0){
            val = val.slice(4,val.length);
            val = JSON.parse(val);
        }
        return val;
    },
    clearKey : function(key,removing){
        if (removing) {
            FExtension.store.getLocalStorage().removeItem(key);
            return;
        }
        if (FExtension.store.getLocalStorage()) { //localStorage){
            FExtension.store.getLocalStorage().setItem(FExtension.config.keyPrefix + key, '');
        }
    },

    setDefault: function(){
	for(var i=0; i<PACK_PARAMS.length; i++){
		var tmp = PACK_PARAMS[i].split(";");
		var curDBname = tmp[0];
		var curDBparam = tmp[1];
		var DBparam = ImTranslatorBG.get(curDBname);
	        if(DBparam == null || DBparam == ""){
			//EXCEPTIONS
			if(curDBname == "SL_change_lang_HK_it"){
				ImTranslatorBG.set(curDBname, curDBparam);
				ImTranslatorBG.set("SL_change_lang_HKbox_it", "true");
			}
			//NONE validator
			if(curDBname != "SL_HK_gt1" && curDBname != "SL_HK_it1" && curDBname != "SL_HK_bb1"){
				ImTranslatorBG.set(curDBname, curDBparam);
			}
			//EXCEPTIONS
		}


                if(curDBname == "SL_LOCALIZATION"){
			if(DBparam == null) ImTranslatorBG.LOC_TABLE();
		}

                if(curDBname.indexOf("SL_ALL_PROVIDERS_")!=-1){
			var pr = ImTranslatorBG.get(curDBname);
			pr = pr.replace(/,undefined/g,"");
			pr = pr.replace(/undefined,/g,"");
			ImTranslatorBG.set(curDBname, pr);
		}


		if(curDBname != "SL_HK_SO_wpt" && ImTranslatorBG.get(curDBname) == "Alt + W"){
			ImTranslatorBG.set(curDBname, FExtension.store.GetFromDefault(curDBname));
		}


		if(curDBname == "SL_HK_CT_wpt"){
			ImTranslatorBG.set(curDBname, FExtension.store.GetFromDefault(curDBname));
		}


	}
	FExtension.store.NONE_validator();
	FExtension.store.DETECT_CONFLICTS_LAST_STAGE(GLOB_PREF);
    },



    VerifyHKs: function(NAME, PARAM){
	for(var i=0; i<PACK_PARAMS.length; i++){
		var tmp = PACK_PARAMS[i].split(";");
		var curDBname = tmp[0];
		var curDBparam = tmp[1];
		if(curDBname != NAME && ImTranslatorBG.get(curDBname) == PARAM){
			ImTranslatorBG.set(curDBname, FExtension.store.GetFromDefault(curDBname));
		}
	}
    },




    GetFromDefault: function(name){
	for(var i=0; i<PACK_PARAMS.length; i++){
		var tmp = PACK_PARAMS[i].split(";");
		var curDBname = tmp[0];
		var curDBparam = tmp[1];
		var DBparam = ImTranslatorBG.get(curDBname);
	        if(curDBname == name) return curDBparam;
  	}
    },

    DETECT_CONFLICTS_LAST_STAGE: function(PREF){
	var HKnames = reservedHK.split(",");
	var NEWarrayHK = new Array();
	for(var i=0; i < HKnames.length; i++){
		NEWarrayHK[i] = ImTranslatorBG.get(PREF+HKnames[i]);
	}
	NEWarrayHK.forEach(function (value, index, arr){
        	let first_index = arr.indexOf(value);
	        let last_index = arr.lastIndexOf(value);
        	if(first_index !== last_index){
        	    if(value!="") {
			var defPar = FExtension.store.GetFromDefault(PREF+HKnames[index]);
			ImTranslatorBG.set(PREF+HKnames[index], defPar);
		    }
        	}
	});
    },


    NONE_validator: function(){
        var out = 0;
	if(ImTranslatorBG.get("SL_HK_gt1")==null || ImTranslatorBG.get("SL_HK_gt1")=="") out++;
	if(ImTranslatorBG.get("SL_HK_it1")==null || ImTranslatorBG.get("SL_HK_it1")=="") out++;
	if(ImTranslatorBG.get("SL_HK_bb1")==null || ImTranslatorBG.get("SL_HK_bb1")=="") out++;
	if(out>1){
		var gt1 = PACK_PARAMS[58].split(";")
		ImTranslatorBG.set("SL_HK_gt1",gt1[1]);
		var it1 = PACK_PARAMS[60].split(";")
		ImTranslatorBG.set("SL_HK_it1",it1[1]);
		var bb1 = PACK_PARAMS[62].split(";")
		ImTranslatorBG.set("SL_HK_bb1",bb1[1]);
	}
    },

    getUPDATES:  function(){

	    var LIST_PR_BBL = FExtension.store.SL_PR_ALL;
	    if(ImTranslatorBG.get("SL_ALL_PROVIDERS_BBL")==null) {
		ImTranslatorBG.set("SL_ALL_PROVIDERS_BBL", LIST_PR_BBL);
	    } else {
	            var BBL = FExtension.store.VerifyProviders(ImTranslatorBG.get("SL_ALL_PROVIDERS_BBL"), LIST_PR_BBL);
		    if(BBL == "") BBL = LIST_PR_BBL; 
		    ImTranslatorBG.set("SL_ALL_PROVIDERS_BBL", BBL);
	    }

	    var LIST_PR_GT = FExtension.store.SL_PR_ALL;
	    if(ImTranslatorBG.get("SL_ALL_PROVIDERS_GT")==null) {
		ImTranslatorBG.set("SL_ALL_PROVIDERS_GT", LIST_PR_GT);
	    } else {
	            var GT = FExtension.store.VerifyProviders(ImTranslatorBG.get("SL_ALL_PROVIDERS_GT"),LIST_PR_GT);
		    if(GT == "") GT = LIST_PR_GT; 
		    ImTranslatorBG.set("SL_ALL_PROVIDERS_GT", GT);
	    }

	    var LIST_PR_IT = FExtension.store.SL_PR_IT;
	    if(ImTranslatorBG.get("SL_ALL_PROVIDERS_IT")==null) {
		ImTranslatorBG.set("SL_ALL_PROVIDERS_IT", LIST_PR_IT);
	    } else {
	            var IT = FExtension.store.VerifyProviders(ImTranslatorBG.get("SL_ALL_PROVIDERS_IT"),LIST_PR_IT);
		    if(IT == "") IT = LIST_PR_IT; 
		    ImTranslatorBG.set("SL_ALL_PROVIDERS_IT", IT);
	    }



	    // NEW PARAMS related to the current version (UPGARDE ONLY)
	        var parNAME = "MoveBBLX"
	        var par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,0);

	        parNAME = "MoveBBLY"
	        par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,0);

	        parNAME = "SL_HK_SObox_wpt"
	        par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,true);

	        parNAME = "SL_HK_CTbox_wpt"
	        par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,true);

	        parNAME = "SL_HK_SO_wpt";
	        var parHK = "Alt + W";
	        par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,parHK);
		FExtension.store.VerifyHKs(parNAME,parHK);

		ImTranslatorBG.set("SL_HK_CT_wpt","Escape");


	        parNAME = "SL_FAV_START"
	        par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,10);

	        parNAME = "SL_FAV_MAX"
	        par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,3);

	        parNAME = "SL_FAV_LANGS_BBL"
	        par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,FExtension.store.SL_BR_LN);

	        parNAME = "SL_FAV_LANGS_IT"
	        par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,FExtension.store.SL_BR_LN);

	        parNAME = "SL_FAV_LANGS_WPT"
	        par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,FExtension.store.SL_BR_LN);

	        parNAME = "SL_FAV_LANGS_IMT"
	        par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,FExtension.store.SL_BR_LN);

	        parNAME = "SL_FAV_TRIGGER"
	        par = ImTranslatorBG.get(parNAME);
		if(par == "" || par == "undefined" || par == null) ImTranslatorBG.set(parNAME,0);

		//CHECK CUSTOM LANGS		
	        parNAME = "SL_LNG_LIST"
	        par = ImTranslatorBG.get(parNAME);
		if(par != "all") {
			par = FExtension.store.CHECK_CUSTOM_LANGS(par);
			ImTranslatorBG.set(parNAME,par);
		}
		//CHECK CUSTOM LANGS

		//CHECK ALL PAIRS
	        parNAME1 = "SL_langSrc";
	        parNAME2 = "SL_langDst";
	        par1 = ImTranslatorBG.get(parNAME1);
	        par2 = ImTranslatorBG.get(parNAME2);
		var out = FExtension.store.GET_PAIR_AVAILABILITY(par1,par2);
		if(out != "") {
			var arr = out.split("/");
			ImTranslatorBG.set(parNAME1,arr[0]);
			ImTranslatorBG.set(parNAME2,arr[1]);
		}

	        parNAME1 = "SL_langSrc_bbl";
	        parNAME2 = "SL_langDst_bbl";
	        par1 = ImTranslatorBG.get(parNAME1);
	        par2 = ImTranslatorBG.get(parNAME2);
		var out = FExtension.store.GET_PAIR_AVAILABILITY(par1,par2);
		if(out != "") {
			var arr = out.split("/");
			ImTranslatorBG.set(parNAME1,arr[0]);
			ImTranslatorBG.set(parNAME2,arr[1]);
		}

	        parNAME1 = "SL_langSrc_it";
	        parNAME2 = "SL_langDst_it";
	        par1 = ImTranslatorBG.get(parNAME1);
	        par2 = ImTranslatorBG.get(parNAME2);
		var out = FExtension.store.GET_PAIR_AVAILABILITY(par1,par2);
		if(out != "") {
			var arr = out.split("/");
			ImTranslatorBG.set(parNAME1,arr[0]);
			ImTranslatorBG.set(parNAME2,arr[1]);
		}

	        parNAME1 = "SL_langSrc_wpt";
	        parNAME2 = "SL_langDst_wpt";
	        par1 = ImTranslatorBG.get(parNAME1);
	        par2 = ImTranslatorBG.get(parNAME2);
		var out = FExtension.store.GET_PAIR_AVAILABILITY(par1,par2);
		if(out != "") {
			var arr = out.split("/");
			ImTranslatorBG.set(parNAME1,arr[0]);
			ImTranslatorBG.set(parNAME2,arr[1]);
		}

		//CHECK ALL PAIRS

		// NO MORE YANDEX
		var PRNAME = "BL_D_PROV";
	        var PR_ = ImTranslatorBG.get(PRNAME);
		if(PR_ == "Yandex") ImTranslatorBG.set(PRNAME,"Translator");

		PRNAME = "BL_T_PROV";
	        PR_ = ImTranslatorBG.get(PRNAME);
		if(PR_ == "Yandex") ImTranslatorBG.set(PRNAME,"Translator");

		PRNAME = "PLD_DPROV";
	        PR_ = ImTranslatorBG.get(PRNAME);
		if(PR_ == "Yandex") ImTranslatorBG.set(PRNAME,"Translator");

		PRNAME = "PLT_PROV";
	        PR_ = ImTranslatorBG.get(PRNAME);
		if(PR_ == "Yandex") ImTranslatorBG.set(PRNAME,"Translator");

		PRNAME = "SL_ALL_PROVIDERS_BBL";
	        PR_ = ImTranslatorBG.get(PRNAME);
		ImTranslatorBG.set(PRNAME,PR_.replace("Yandex","")); 

		PRNAME = "SL_ALL_PROVIDERS_GT";
	        PR_ = ImTranslatorBG.get(PRNAME);
		ImTranslatorBG.set(PRNAME,PR_.replace("Yandex","")); 

		PRNAME = "SL_ALL_PROVIDERS_IT";
	        PR_ = ImTranslatorBG.get(PRNAME);
		ImTranslatorBG.set(PRNAME,PR_.replace("Yandex","")); 
		// NO MORE YANDEX

	    // NEW PARAMS 
    },

    CHECK_CUSTOM_LANGS: function(LIST){
	try{
		var OUT=LIST;
		var tmpOUT = "";
		var lngarr = LISTofPRpairsDefault.split(",");
		var tmp = LIST.split(",");	
		var cnt = 0;
		for(var i=0; i<lngarr.length; i++){
			for(var j=0; j<tmp.length; j++){
				if(lngarr[i]==tmp[j]){                                                                                                                                                            2
					tmpOUT = tmpOUT + tmp[j] + ",";
					cnt++;
				}
			}
		}
                if(tmp[0]=="auto") {
			cnt++;
			tmpOUT = "auto," + tmpOUT;
		}
		OUT = tmpOUT;
		if(OUT=="" || cnt<=1) OUT="all";
		else OUT = OUT.replace(/,(?=[^,]*$)/, '');
		return(OUT);
	} catch(ex){}
    },

    GET_PAIR_AVAILABILITY: function(p1, p2){
	try{
		var OUT = "";
		var OUT1 = "";
		var OUT2 = "";
		var LIST = ImTranslatorBG.get(GLOB_PREF + "_LNG_LIST")
		if(LIST == "all") {
			var lngarr = LISTofPRpairsDefault.split(",");
			for(var i=1; i<lngarr.length; i++){
				var tmp = lngarr[i].split(":");	
				if(tmp[0].toLowerCase()==p1.toLowerCase()) OUT1 = p1;
				if(tmp[0].toLowerCase()==p2.toLowerCase()) OUT2 = p2;
			}
		
			if(OUT1 != "" && OUT2 !="" && OUT1 != OUT2) OUT = OUT1+"/"+OUT2;
			if(OUT1 == "" && OUT2 == "") OUT = "auto/"+FExtension.store.SL_BR_LN;
			if(OUT1 == "" && OUT2 != "") OUT = "auto/"+OUT2;
			if(OUT1 != "" && OUT2 == "") {
				for(var i=1; i<lngarr.length; i++){
					var tmp = lngarr[i].split(":");	
					if(OUT1 != tmp[0].toLowerCase()){
						OUT = OUT1 + "/" + tmp[0];
						i=10000;
					}
				}
			}
		} else {
			var lngarr = LIST.split(",");
			for(var i=0; i<lngarr.length; i++){
				if(lngarr[i].toLowerCase()==p1.toLowerCase()) OUT1 = p1;
				if(lngarr[i].toLowerCase()==p2.toLowerCase()) OUT2 = p2;
			}

			if(OUT1 != "" && OUT2 !="" && OUT1 != OUT2) OUT = OUT1+"/"+OUT2;
			if(OUT1 == "" && OUT2 == "") OUT = lngarr[0]+"/"+lngarr[1];
			if(OUT1 == "" && OUT2 != "") {
				for(var i=0; i<lngarr.length; i++){
					if(OUT2 != lngarr[i].toLowerCase()){
						OUT = lngarr[i] + "/" + OUT2;
						i=10000;
					}
				}
			}
			if(OUT1 != "" && OUT2 == "") {
				for(var i=0; i<lngarr.length; i++){
					if(OUT1 != lngarr[i].toLowerCase()){
						OUT = OUT1 + "/" + lngarr[i];
						i=10000;
					}
				}
			}
		}
		if(OUT == "" && LIST != ""){
			var lngarr = LIST.split(",");
			OUT = lngarr[0] + "/" + lngarr[1];
		}
		return(OUT);
		
	} catch(ex){}
    },


    save_LOC4CONTEXT: function(){
          var tmp = FExtension.element(ImTranslatorBG.get('SL_LOCALIZATION'),'extLanguages').split(",")
	  var bbl = ImTranslatorBG.get("SL_langDst_bbl");
	  var it = ImTranslatorBG.get("SL_langDst_it");
	  var wpt = ImTranslatorBG.get("SL_langDst_wpt");
	  var gt = ImTranslatorBG.get("SL_langDst");
	  var tmp2;
	  for (var i=0; i<tmp.length; i++){
	      tmp2 = tmp[i].split(":");
	      if(tmp2[0]==bbl) ImTranslatorBG.set("SL_langDst_name_bbl", encodeURIComponent(tmp2[1]));
	      if(tmp2[0]==it) ImTranslatorBG.set("SL_langDst_name_it", encodeURIComponent(tmp2[1]));
	      if(tmp2[0]==wpt) ImTranslatorBG.set("SL_langDst_name_wpt", encodeURIComponent(tmp2[1]));
	      if(tmp2[0]==gt) ImTranslatorBG.set("SL_langDst_name", encodeURIComponent(tmp2[1]));
	  }
    },

    SL_isMacintosh: function() {
	  return navigator.platform.indexOf('Mac') > -1;
    },                                                                     

    SL_isLinux: function() {
        var OSName = false;
	if (navigator.appVersion.indexOf("X11")!=-1) OSName=true;
	if (navigator.appVersion.indexOf("Linux")!=-1) OSName=true;
	return OSName;
    },


    VerifyProviders: function(oldLIST,newLIST) {
	var out = "";
	var oldST = oldLIST.split(",");
	var newST = newLIST.split(",");
 	if(oldST.length>=newST.length){
		for(var i=0; i<oldST.length;i++){
			for(var j=0; j<newST.length;j++){
				if(oldST[i]==newST[j]) out=out+oldST[i]+",";
			}
		}	
		out = out.substring(0,out.length-1);
	} else {
		for(var i=0; i<oldST.length;i++){
		        if(newLIST.indexOf(oldST[i])!=-1) newLIST = newLIST.replace(oldST[i],"");
		}	
		newLIST = newLIST.replace(/,/g," ");
		newLIST = newLIST.replace(/\s\s+/g, '');
		out = oldLIST +","+ newLIST;
	}
	return out;
    }


};

}catch(ex){
//	FExtension.alert_debug(ex);
}