$(document).ready(function() {
    function getCurrent() {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                console.log(xhr.response);
            }
        }
        xhr.open('GET', 'http://localhost:5000/current');
        xhr.send();
        console.log('hey here')
        setTimeout(getCurrent, 2000);
    }

    setTimeout(getCurrent, 2000);
});