var socket = io();

// ===================== HANDLE DISCONNECT MESSAGE =====================
// Kirim event disconnect ke server saat user keluar/refresh halaman
window.onbeforeunload = function () {
  socket.emit("client_disconnecting", {});
};

// ===================== HANDLE RECEIVED MESSAGE =======================
// Terima pesan dari server dan render ke chatbox
socket.on("message", function (data) {
  let content = "";

  // Render pesan sesuai pengirim (kanan/kiri/server)
  if (data.username == username_user) {
    content =
      '<div class="msg right-msg"><div class="msg-bubble"><div class="msg-info"><div class="msg-info-name">' +
      data.username +
      '</div><div class="msg-info-time">' +
      data.time +
      '</div></div><div class="msg-text">' +
      data.msg +
      "</div></div></div>";
  } else if (data.username != username_user) {
    if (data.username === "Chocalate Server") {
      content =
        '<div class="msg left-msg server"><div class="msg-bubble"><div class="msg-info"><div class="msg-info-name">' +
        data.username +
        '</div><div class="msg-info-time">' +
        data.time +
        '</div></div><div class="msg-text">' +
        data.msg +
        "</div></div></div>";
    } else {
      content =
        '<div class="msg left-msg"><div class="msg-bubble"><div class="msg-info"><div class="msg-info-name">' +
        data.username +
        '</div><div class="msg-info-time">' +
        data.time +
        '</div></div><div class="msg-text">' +
        data.msg +
        "</div></div></div>";
    }
  }

  // Tampilkan pesan jika tidak kosong
  if (data.msg !== "") {
    $("#chatbox-chat").append(content);
  }

  // Render daftar user di modal user
  if (Array.isArray(data.users_username)) {
    let txt = "";
    data.users_username.forEach(function (value) {
      txt +=
        '<div class="mb-1 mt-1 border d-flex"><img class="m-3" src="/static/assets/Images/account_3033143.png" alt="" height="20px"><p class="mt-3">' +
        value +
        "</p></div><br/>";
    });
    let result = txt.substr(0, txt.length - 5);
    $(".user-modal-body").html(result);
  } else {
    $(".user-modal-body").html(
      '<div class="mb-1 mt-1 border"><img class="m-3" src="/static/assets/Images/account_3033143.png" alt="" height="20px"><p class="mt-3">' +
        data.users_username +
        "</p></div><br/>"
    );
  }

  // Scroll ke pesan terakhir
  $(".msg").last()[0].scrollIntoView();

  // Tampilkan indikator typing
  let indicator =
    '<div class="indicator mt-1 ms-2 blink-soft" id="' +
    data.username +
    '"><small>&nbsp;' +
    data.username +
    " is typing.</small></div>";

  let span_typing =
    "<div id='dash-indicator'><span></span><span></span><span></span></div>";

  if (data.status == "now typing") {
    $(".notif-modal-body").append(indicator);
    $(".typing-indicator").append(span_typing);
    $("#typing-notif").css("display", "inline-block"); // Tampilkan ikon
    if ($(".notif-modal-body .blink-soft").length > 0) {
      $("#typing-notif").addClass("blink-soft");
    }
  } else if (data.status == "done typing") {
    $("#" + data.username).remove();
    $("#dash-indicator").remove();
    if ($(".notif-modal-body .blink-soft").length === 0) {
      $("#typing-notif").removeClass("blink-soft");
      $("#typing-notif").css("display", "none"); // Sembunyikan ikon
    }
    //$("#typing-notif").css("display", "none");
    //$("#typingNotifModal").modal("hide");
  }
});

// ===================== FUNCTION TO SEND MESSAGE ======================
// Fungsi kirim pesan ke server
function SendMessage() {
  const btn = document.querySelector(".chatbox-send-btn");
  btn.classList.remove("animated"); // reset jika animasi masih berjalan
  void btn.offsetWidth; // force reflow
  btn.classList.add("animated");

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

// ===================== TYPING INDICATOR ==============================
// Kirim status typing ke server saat user mengetik
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

    if (!elementClicked) {
      if (!typing) {
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

// ===================== TAB AT TEXT AREA ==============================
// Tambahkan karakter tab saat user menekan tombol Tab di textarea
document.getElementById("message").addEventListener("keydown", function (e) {
  if (e.key == "Tab") {
    e.preventDefault();
    var start = this.selectionStart;
    var end = this.selectionEnd;
    this.value =
      this.value.substring(0, start) + "\t" + this.value.substring(end);
    this.selectionStart = this.selectionEnd = start + 1;
  }
});
