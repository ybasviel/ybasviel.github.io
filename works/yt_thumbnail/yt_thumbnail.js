const change = document.getElementById("change");
const input = document.querySelector("input");

const sdimg = document.querySelector("sd");
const hdimg = document.querySelector("hd");

const sd_link = document.getElementById("sd_link");
const hd_link = document.getElementById("hd_link");


let sdimg_url = "";
let hdimg_url = "";

let youtube_id = "";
let youtube_ids = [];

function rewrite()
{
    youtube_ids = input.value.split(/[=,/]/);
    youtube_id = youtube_ids[youtube_ids.length-1];

    sdimg_url = "http://img.youtube.com/vi/" + youtube_id + "/sddefault.jpg";
    sd_link.href = sdimg_url;
    sd_link.download = youtube_id + ".jpg"
    sd.src = sdimg_url;

    hdimg_url = "http://img.youtube.com/vi/" + youtube_id + "/maxresdefault.jpg"
    hd_link.href = hdimg_url;
    hd_link.download = youtube_id + ".jpg"
    hd.src = hdimg_url;
}

change.addEventListener("click", rewrite);
