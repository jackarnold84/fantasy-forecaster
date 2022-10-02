
function sleep(s) {
    return new Promise(resolve => setTimeout(resolve, s * 1000));
}


function sum(arr) {
    return arr.reduce((a, b) => a + b, 0)
}


function randInt(upper) {
    return Math.floor(Math.random() * upper)
}


function printEntries(obj) {
    for (let key in ob) {
        console.log(key);
    }
}
