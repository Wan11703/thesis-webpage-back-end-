const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const util = require('util');
const e = require('express');
const unlinkFile = util.promisify(fs.unlink);

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, './public/uploads')
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9)
        cb(null, uniqueSuffix + path.extname(file.originalname))
    }
})

const upload = multer({
    storage: storage,
    limits: { fileSize: 5000000 }, // 5MB limit
    fileFilter: function (req, file, cb) {
        checkFileType(file, cb);
    }
}).any();

function checkFileType(file, cb) {
    const fileTypes = /jpeg|jpg|png/;
    const extname = fileTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = fileTypes.test(file.mimetype);

    if (mimetype && extname) {
        return cb(null, true);
    } else {
        cb('Please upload images only!');
    }

}

const port = 3000;

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.set('view engine', 'ejs');

app.use(express.static("public"));

app.get("/", (req, res) => {
    res.render("index");
});

app.post("/upload", (req, res) => {
    upload(req, res, (err) => {
        if (!err && req.files != "") {
            res.status(200).send()
        }else if (!err && req.files == "") {
            res.statusMessage = 'Please select an image to upload!'
            res.status(400).end()
        }
        else{
            res.statusMessage = (err === 'Please upload images only!') ? err : 'Photo exceeds 1MB limit!'
            res.status(400).end()
        }
    })

})

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});