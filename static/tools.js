result = {
    code: 0,
    data: '',
    success: false
}

get = (url, callback) => {
    xmlHttp = new XMLHttpRequest()
    if(xmlHttp != null){
        xmlHttp.open('GET', url)
        xmlHttp.onreadystatechange = function(){
            buildResult(xmlHttp, callback)
        }
    }
}

post = (url, formData, callback) => {
    xmlHttp = new XMLHttpRequest()
    if(xmlHttp != null){
        xmlHttp.open('POST', '/login')
        xmlHttp.send(formData)
        xmlHttp.onreadystatechange = function(){
            buildResult(xmlHttp, callback)
        }
    }
}

buildResult = (xmlHttp, callback) => {
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
        text = xmlHttp.responseText
        console.log(text)
        callback({
            code: 1,
            data: xmlHttp.responseText,
            success: true
        })
    } else {
        text = xmlHttp.responseText
        console.log(text)
        callback({
            code: 0,
            data: xmlHttp.responseText,
            success: false
        })
    }
}
