statify.deployForm = {
    onSubmit: function(e) {
        var $form = $(this),
            $submitBtn = $form.find('input[name="_save"]'),
            $loader = $form.find('.loader');
            $selectBox = $form.find('select'),
            $cancelBtn = $form.find('.deletelink');

        $submitBtn.val($submitBtn.attr('data-value')).attr('disabled', 'disabled');
        setTimeout(function(){ $selectBox.attr('disabled', 'disabled'); }, 50);
        $cancelBtn.hide();
        $loader.show();
    },

    setup: function(o) {
        var $obj = $(o.selector),
            $form = $obj.find('form#release_deploy_form');

        $form.bind('submit', statify.deployForm.onSubmit);
    },

    init: function() {
        statify.deployForm.setup({
            selector: '[data-fn="deployForm"]'
        });
    }
};

statify.deployForm.init();


statify.releaseList = {
    server: null,

    onAddBtnClick: function(e) {
        var $btn = $(this),
            $loader = $btn.parent().find('.loader');
        $loader.show();
    },

    onPreviewBtnClick: function(e) {
        e.preventDefault();

        var $this = $(this),
            $previewBtns = $('.preview'),
            $stopBtn = $('<a href="/admin/statify/release/preview/stop/">Stop</a>'),
            $showBtn = $('<a href="http://127.0.0.1:8080/" target="_blank">Show</a>');

        $previewBtns.hide();

        statify.releaseList.server = $.ajax({ url: $this.attr('href') });

        $stopBtn.bind('click', statify.releaseList.stopPreview).parent();
        $this.parent().append($stopBtn, $('<span> | </span>'), $showBtn);
    },

    stopPreview: function(e) {
        e.preventDefault();

        var $this = $(this),
            $previewBtns = $('.preview');

        $previewBtns.show();

        statify.releaseList.server.abort();
        $(this).remove();

        $.get($this.attr('href'));
    },

    setup: function(o) {
        var $obj = $(o.selector),
            $addBtn = $obj.find('.addlink'),
            $previewBtn = $obj.find('.preview');

        $addBtn.bind('click', statify.releaseList.onAddBtnClick);
        $previewBtn.bind('click', statify.releaseList.onPreviewBtnClick);
    },

    init: function() {
        statify.releaseList.setup({
            selector: '[data-fn="releaseList"]'
        });
    }
};

statify.releaseList.init();

