// Mock Telegram WebApp for browser preview & ensure valid auth
(function() {
  var mockInitData = "query_id=AAH12345&user=%7B%22id%22%3A999999999%2C%22first_name%22%3A%22Rolls%20Player%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22player%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%7D&auth_date=1793280000&hash=mockhash12345";
  
  try {
    if (!sessionStorage.getItem("query_id")) {
      sessionStorage.setItem("query_id", mockInitData);
    }
  } catch(e) {}

  if (!window.Telegram) {
    window.Telegram = {};
  }
  
  if (!window.Telegram.WebApp || !window.Telegram.WebApp.initData) {
    var webApp = window.Telegram.WebApp || {};
    webApp.initData = mockInitData;
    webApp.initDataUnsafe = {
      query_id: "AAH12345",
      user: {
        id: 999999999,
        first_name: "Rolls Player",
        last_name: "",
        username: "player",
        language_code: "en",
        is_premium: true
      },
      auth_date: "1793280000",
      hash: "mockhash12345"
    };
    webApp.version = "8.0";
    webApp.platform = "tdesktop";
    webApp.colorScheme = "dark";
    webApp.themeParams = {
      bg_color: "#101115",
      text_color: "#ffffff",
      hint_color: "#708499",
      link_color: "#6ab3f3",
      button_color: "#5288c1",
      button_text_color: "#ffffff",
      secondary_bg_color: "#181a20"
    };
    webApp.isExpanded = true;
    webApp.viewportHeight = window.innerHeight;
    webApp.viewportStableHeight = window.innerHeight;
    webApp.headerColor = "#101115";
    webApp.backgroundColor = "#101115";
    webApp.BackButton = {
      isVisible: false,
      onClick: function() {},
      offClick: function() {},
      show: function() {},
      hide: function() {}
    };
    webApp.MainButton = {
      text: "CONTINUE",
      color: "#5288c1",
      textColor: "#ffffff",
      isVisible: false,
      isActive: true,
      setText: function() {},
      onClick: function() {},
      offClick: function() {},
      show: function() {},
      hide: function() {},
      enable: function() {},
      disable: function() {}
    };
    webApp.HapticFeedback = {
      impactOccurred: function() {},
      notificationOccurred: function() {},
      selectionChanged: function() {}
    };
    webApp.ready = function() {};
    webApp.expand = function() {};
    webApp.close = function() {};
    webApp.openLink = function(url) { window.open(url, "_blank"); };
    webApp.openTelegramLink = function(url) { window.open(url, "_blank"); };
    webApp.showAlert = function(msg, cb) { alert(msg); if(cb) cb(); };
    webApp.showConfirm = function(msg, cb) { var r = confirm(msg); if(cb) cb(r); };
    webApp.onEvent = function() {};
    webApp.offEvent = function() {};
    webApp.sendData = function() {};
    webApp.requestFullscreen = function() {};
    webApp.isVersionAtLeast = function() { return true; };
    window.Telegram.WebApp = webApp;
  }
})();
