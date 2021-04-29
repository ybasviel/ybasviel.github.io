const change = document.getElementById("change");
const input = document.querySelector("input");
const sdimg = document.querySelector("sd");
const hdimg = document.querySelector("hd");


let sdimg_url = "";
let hdimg_url = "";

let youtube_id = "";
let youtube_ids = [];

function rewrite()
{
    youtube_ids = input.value.split(/[=,/]/);
    youtube_id = youtube_ids[youtube_ids.length-1];

    sdimg_url = "http://img.youtube.com/vi/" + youtube_id + "/sddefault.jpg";
    sd.src = sdimg_url;

    hdimg_url = "http://img.youtube.com/vi/" + youtube_id + "/maxresdefault.jpg"
    hd.src = hdimg_url;
}

change.addEventListener("click", rewrite);
