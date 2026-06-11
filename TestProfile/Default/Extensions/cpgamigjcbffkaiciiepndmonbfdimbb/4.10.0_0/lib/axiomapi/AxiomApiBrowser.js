import {AxiomApiUtilities} from "./AxiomApiUtilities"
import Papa from "papaparse"

/**
 * Interact with the browser directly.
 */
export class AxiomApiBrowser {
    /**
     * Retrieve all of the cookies from a specified page.
     * @param url URL of the page to grab cookies from.
     * @param callback Callback function, receiving one parameter containing the retrieved cookie data.
     * @example AxiomApiBrowser.getCookies("http://www.myurl.com", cookies => { // do something }
     */
    static getCookies(url, callback) {
        const urls = (!Array.isArray(url)) ? [url] : url
        const urlString = urls.join('')
        chrome.cookies.getAll({}, res => {
            const cookies = res.filter(cookie => {
                return (new RegExp(cookie.domain)).test(urlString)
            })
            callback(cookies)
        })
    }

    static getUsedCookies(widgets, callback) {
        let urls = []
        for (let w of widgets) {
            for (let p of w.params) {
                if (p.type.indexOf('url') !== -1) {
                    urls.push(p.value)    
                }
            }
        }
        AxiomApiBrowser.getCookies(urls, cookies => {
            callback(cookies)
        })
    }

    static async getStorageValues(urls) {
        let ls = {}
        for (let url of urls) {
            if (url.indexOf('http') !== 0) {
                url = 'https://' + url
            }
            let domain = url.replace('http://','').replace('https://','').split(/[/?#]/)[0];
            if (!ls.hasOwnProperty(domain)) {
                ls[domain] = await this.loadStorageFromTab(url)
            }
        }

        return ls
    }

    static async loadStorageFromTab(url) {
        // Not ideal, but this is apparently the API chosen for Chrome V3 manifest...
        function getStorageFunc() {
            let lst = {};
            let sst = {};
            for (let k in localStorage) {
                lst[k] = localStorage.getItem(k);
            }
            for (let k in sessionStorage) {
                sst[k] = sessionStorage.getItem(k);
            }
            const data = {session: sst, local: lst};
            return data
        }
        return await new Promise((resolve, reject) => {
            chrome.tabs.create({
                active: false,
                url: url
            }, function(tab) {
                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    func: getStorageFunc
                }, function(result) {
                    chrome.tabs.remove(tab.id)
                    if (Array.isArray(result) && result.length > 0 && result[0].result) {
                        resolve (result[0].result)
                    } else {
                        resolve ({})
                    }
                })
            })
        })
    }

    static messageAccept(res, accept) {
        accept(res)
    }

    static grabCurrentUrl(callback) {
        callback(window.location.href)
    }

    /**
     * Display a message in a popup window. Execution continues after user confirms.
     * @param message Message to display.
     * @param accept Function to call when the user clicks 'OK'.
     */
    static displayMessage(message, callback, helper = this.messageAccept) {
        let ok = (res) => {
            helper("user-accepted", callback)
        }
        $.confirm({ 
            title: "", 
            backgroundDismiss: true, 
            content: message,
            buttons: {
                ok: {
                    text: "OK",
                    action: ok
                },
                cancel: {
                    text: "Cancel",
                    action: () => {callback({error: "User cancelled"})}
                }
            },
            backgroundDismiss: function(){
                callback({error: "User cancelled"})
            },
            autoClose: 'ok|10000'
        })
    }
    /**
     * Create a form for entering values at runtime.
     * @param name The unique of the form
     * @param title The title to display to the user
     * @param form An array of objects describing the form.
     * @param callback Callback function, receiving one parameter containing the results of the form submission.
     * @example AxiomApiBrowser.displayForm("myform", "My Form", [{type: "textfield", label: "Text Field", name: "textfield"}], values => console.log(values))
     */
    static displayForm(name, title, form, callback) {
        let formStr = `<form id="${name}" onsubmit="return false;">`
        for (const f of form) {
            switch (f.type) {
                case "textfield":
                    if(f.placeholder === 'File Path') {
                        formStr += `<label style="display: block;">${f.label}</label><input type="textfield" name="${f.name}" placeholder="${f.value}" value="${f.value}" class="form-field" onkeypress="if(event.keyCode == 13) { $('.btnsbmt').click(); return null; }"/><br/>`
                    } else {
                        formStr += `<label style="display: block;">${f.label}</label><input type="textfield" name="${f.name}" placeholder="${f.placeholder}" class="form-field" onkeypress="if(event.keyCode == 13) { $('.btnsbmt').click(); return null; }"/><br/>`
                    }
                    break
                case "textarea":
                    formStr += `<label style="display: block;">${f.label}</label><textarea name="${f.name}" rows="5" class="form-field"></textarea><br/>`
                    break
                case "text_data_list_to_array":
                    formStr += `<label style="display: block;">${f.label}</label><textarea ax-type="data_list" name="${f.name}" rows="5" class="form-field" on></textarea><br/>`
                    break
            }
        }
        formStr += "</form>"
        $.confirm({title: title, backgroundDismiss: true, content: formStr, draggable: false,
            buttons: {
                specialKey: {
                    isHidden: true,
                    text: 'On behalf of enter',
                    keys: ['enter'],
                    action: () => {
                        $('.btnsbmt').click()
                        return null;
                    }
                },
                formSubmit: {
                    text: 'Submit',
                    btnClass: 'btn-blue btnsbmt',
                    action: () => {
                        const values = {};
                        $("#" + name + " .form-field").each(function() {
                            if ($(this).attr('ax-type') && $(this).attr('ax-type') == 'data_list') {
                                let filteredData = AxiomApiUtilities.convertListToArray($(this).val());
                                values[$(this).attr("name")] = filteredData;
                            } else {
                                values[$(this).attr("name")] = $(this).val();
                            }
                        })
                        callback(values);
                    }
                },
                cancel: {
                    text: 'Cancel',
                    action: () => {callback({error: "User cancelled"})}
                }
            },
            backgroundDismiss: function(){
                return 'cancel';
            },
        })
    }

    /**
     * Apply a style to the given selector.
     * @param selector
     * @param styles
     */
    static style(selector, styles) {
        $(selector).style(styles)
    }

    /**
     * Display data as a popup. Generates a nested list.
     * @param data A javascript object or array containing some data.
     * @example AxiomApiBrowser.displayData({foo: "bar"})
     */
    static displayData(data, callback) {
        AxiomApiBrowser.displayMessage(dataToList("", "Data", data), callback)
    }

    /**
     * Export token to CSV file
     * @param arr
     */
    static generateCSV(arr, filename = 'export.csv') {
        let csvFile
        const output = Papa.unparse(arr)
        csvFile = new Blob([output], { type: "text/csv" })
        this.downloadCSV(csvFile, filename)
    }

    /**
     * Download CSV file Automatically
     * @param csvFile blob
     */
    static downloadCSV(csvFile, filename){
        let downloadCSV
        let fileName = filename
        downloadCSV = document.createElement("a")
        downloadCSV.download = fileName
        downloadCSV.href = window.URL.createObjectURL(csvFile)
        downloadCSV.style.display = "none"
        document.body.appendChild(downloadCSV)
        downloadCSV.click()
        document.body.removeChild(downloadCSV)
    }

    /**
     * Create a confirmation model for scheduler
     */
    static displaySchedulerConfirmation(name, formContent, callback) {
        $.confirm({title: 'Confirm', backgroundDismiss: false, content: formContent, draggable: false,minHeight: 100,
            maxHeight: 200,
            autoClose: 'formSubmit|10000',
            buttons: {
                formSubmit: {
                    text: 'Yes',
                    btnClass: 'btn-blue btnsbmt',
                    action: () => {
                        callback({
                            msg: "true"
                        })
                    }
                },
                removeScheduler: {
                    text: 'No and remove this schedule',
                    btnClass: 'btn-red btnsbmt',
                    action: () => {
                        callback({
                            msg: "remove"
                        })
                    }
                },
                cancel: {
                    text: 'No',
                    action: () => {callback({
                        msg: "false"
                    })}
                }
            }
        })
    }

    /**
     * Capture the current page HTML with inline styles and resources
     * @returns {Promise<string>} Complete HTML content
     */
    static async capturePageHTML() {
        const docClone = document.cloneNode(true);
        
        // Remove Axiom extension elements
        docClone.querySelectorAll('.axiom-draw').forEach(el => el.remove());
        
        // Inline all stylesheets
        let inlinedStyles = '';
        for (const sheet of document.styleSheets) {
            try {
                if (sheet.href && sheet.href.includes('chrome-extension')) continue;
                const rules = Array.from(sheet.cssRules || []);
                for (const rule of rules) {
                    inlinedStyles += rule.cssText + '\n';
                }
            } catch (e) {}
        }
        
        // Replace style tags with consolidated styles
        docClone.querySelectorAll('style').forEach(tag => tag.remove());
        const head = docClone.querySelector('head');
        if (head && inlinedStyles) {
            const styleElement = docClone.createElement('style');
            styleElement.textContent = inlinedStyles;
            head.insertBefore(styleElement, head.firstChild);
        }
        
        // Convert images to base64
        const images = docClone.querySelectorAll('img');
        await Promise.all(Array.from(images).map(async (img, index) => {
            const originalImg = document.querySelectorAll('img')[index];
            if (!originalImg || !originalImg.src || originalImg.src.startsWith('data:')) return;
            
            try {
                const canvas = document.createElement('canvas');
                canvas.width = originalImg.naturalWidth || originalImg.width;
                canvas.height = originalImg.naturalHeight || originalImg.height;
                canvas.getContext('2d').drawImage(originalImg, 0, 0);
                img.src = canvas.toDataURL('image/png');
            } catch (e) {}
        }));
        
        return '<!DOCTYPE html>\n' + docClone.documentElement.outerHTML;
    }

    /**
     * Download HTML content as a file
     * @param {string} htmlContent The HTML content to download
     * @param {string} filename Optional custom filename
     */
    static downloadHTML(htmlContent, filename = null) {
        if (!filename) {
            const title = document.title.replace(/[^a-z0-9]/gi, '-').toLowerCase();
            filename = title ? `${title}.html` : 'page-export.html';
        }
        
        const blob = new Blob([htmlContent], { type: "text/html" });
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(link.href);
    }

}
