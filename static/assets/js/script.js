jQuery(document).ready(function () {
  // Tampilkan chatbox saat salah satu chat-list diklik
  $(".chat-list a").click(function () {
    $(".chatbox").addClass("showbox");
    return false;
  });

  // Sembunyikan chatbox saat ikon chat diklik
  $(".chat-icon").click(function () {
    $(".chatbox").removeClass("showbox");
  });
});
