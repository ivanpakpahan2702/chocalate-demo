var socket = io();

//==========================================================================================
//===================== HANDLING DISCONNECT MESSAGE ========================================
//==========================================================================================
//==================================START===================================================
window.onbeforeunload = function () {
    socket.emit("client_disconnecting", {});
};
//==================================END=====================================================
//==========================================================================================
//===================== HANDLING DISCONNECT MESSAGE ========================================
//==========================================================================================

//==========================================================================================
//===================== HANDLING RECEIVED MESSAGE ==========================================
//==========================================================================================
//==================================START===================================================
socket.on("message", function (data) {
    if (data.username == username_user) {
        content =
            '<div class="msg right-msg"> <div class="msg-bubble"><div class="msg-info"><div class="msg-info-name">' +
            data.username +
            '</div><div class="msg-info-time">' +
            data.time +
            '</div></div><div class="msg-text">' +
            data.msg +
            "</div></div></div>";
    } else if (data.username != username_user) {
        if (data.username === "Chocalate Server") {
            content =
                '<div class="msg left-msg server"> <div class="msg-bubble"><div class="msg-info"><div class="msg-info-name">' +
                data.username +
                '</div><div class="msg-info-time">' +
                data.time +
                '</div></div><div class="msg-text">' +
                data.msg +
                "</div></div></div>";
        } else {
            content =
                '<div class="msg left-msg"> <div class="msg-bubble"><div class="msg-info"><div class="msg-info-name">' +
                data.username +
                '</div><div class="msg-info-time">' +
                data.time +
                '</div></div><div class="msg-text">' +
                data.msg +
                "</div></div></div>";
        }
    }

    if (data.msg !== "") {
        $("#chatbox-chat").append(content);
    }

    if (Array.isArray(data.users_username)) {
        let txt = "";
        data.users_username.forEach(accessing_array);

        let string_length = txt.length;
        let result = txt.substr(0, string_length - 5);

        $(".user-modal-body").html(result);

        function accessing_array(value) {
            txt +=
                '<div class="mb-1 mt-1 border d-flex"><img class="m-3" src="/static/assets/Images/account_3033143.png" alt="" height="20px"><p class="mt-3">' +
                value +
                "</p></div><br/>";
        }
    } else {
        $(".user-modal-body").html(
            '<div class="mb-1 mt-1 border"><img class="m-3" src="/static/assets/Images/account_3033143.png" alt="" height="20px"><p class="mt-3">' +
            data.users_username +
            "</p></div><br/>"
        );
    }
    $(".msg").last()[0].scrollIntoView();

    indicator =
        '<div class="indicator mt-1 ms-2 blink-soft" id="' +
        data.username +
        '"><small>&nbsp;' +
        data.username +
        " is typing.</small></div>";

    span_typing =
        "<div id='dash-indicator'><span></span><span></span><span></span></div>";

    if (data.status == "now typing") {
        $(".notif-modal-body").append(indicator);
        $(".typing-indicator").append(span_typing);
        $("#typing-notif").css("display", "inline-block");
    } else if (data.status == "done typing") {
        $("#" + data.username).remove();
        $("#dash-indicator").remove();
        //$("#typing-notif").css("display", "none"); #}
        // $("#typingNotifModal").modal("hide");
    }
});
//==================================END=====================================================
//==========================================================================================
//===================== HANDLING RECEIVED MESSAGE ==========================================
//==========================================================================================

//==========================================================================================
//===================== FUNCTION TO SEND MESSAGE ===========================================
//==========================================================================================
//================================START=====================================================
function SendMessage() {
    var currentdate = new Date();
    var datetime =
        currentdate.getDate() +
        "/" +
        (currentdate.getMonth() + 1) +
        "/" +
        currentdate.getFullYear() +
        "-" +
        currentdate.getHours() +
        ":" +
        currentdate.getMinutes() +
        ":" +
        currentdate.getSeconds();
    if ($("#message").val() != "") {
        socket.send({
            username: username_user,
            msg: $("#message").val(),
            time: datetime,
        });
        $("#message").val("");
    }
}
//================================END=======================================================
//==========================================================================================
//===================== FUNCTION TO SEND MESSAGE ===========================================
//==========================================================================================

//==========================================================================================
//===================== TYPING INDICATOR====================================================
//==========================================================================================
//================================START=======================================================
$(function () {
    var theText = $("#message");
    var typing = false;
    var timeout = undefined;
    var elementClicked = false;

    function timeoutFunction() {
        typing = false;
        socket.emit("client_done_typing", {});
        console.log("done...");
    }

    theText.keydown(function (event) {
        $("#button").click(function () {
            elementClicked = true;
        });

        if (elementClicked != true) {
            if (typing == false) {
                typing = true;
                socket.emit("client_now_typing", {});
                console.log("typing...");
                timeout = setTimeout(timeoutFunction, 1000);
            } else {
                clearTimeout(timeout);
                timeout = setTimeout(timeoutFunction, 1000);
            }
        } else {
            typing = false;
            socket.emit("client_done_typing", {});
            console.log("done...");
        }
    });
});

//================================END=======================================================
//==========================================================================================
//===================== TYPING INDICATOR ===================================================
//==========================================================================================

//==========================================================================================
//===================== TAB AT TEXT AREA ===================================================
//================================START=====================================================
//==========================================================================================

document.getElementById("message").addEventListener("keydown", function (e) {
    if (e.key == "Tab") {
        e.preventDefault();
        var start = this.selectionStart;
        var end = this.selectionEnd;

        // set textarea value to: text before caret + tab + text after caret
        this.value =
            this.value.substring(0, start) + "\t" + this.value.substring(end);

        // put caret at right position again
        this.selectionStart = this.selectionEnd = start + 1;
    }
});
  //================================END=======================================================
  //==========================================================================================
  //===================== TAB AT TEXT AREA ===================================================
  //==========================================================================================