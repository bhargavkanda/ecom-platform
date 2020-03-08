$(document).ready(function() {
  var result;
  'use strict';
  var console = window.console || { log: function () {} };
  var $image = $('#crop-image');
  // var $download = $('#download');
  var imgs = {}
  var $dataX = $('#dataX');
  var $dataY = $('#dataY');
  var $dataHeight = $('#dataHeight');
  var $dataWidth = $('#dataWidth');
  var $dataRotate = $('#dataRotate');
  var $dataScaleX = $('#dataScaleX');
  var $dataScaleY = $('#dataScaleY');
  var options = {
        preview: '.pri-overlay.image .preview',
        zoomable: false,
        strict: true,
        crop: function (e) {
          console.log(e)
          $dataX.val(Math.round(e.x));
          $dataY.val(Math.round(e.y));
          $dataHeight.val(Math.round(e.height));
          $dataWidth.val(Math.round(e.width));
          $dataRotate.val(e.rotate);
          $dataScaleX.val(e.scaleX);
          $dataScaleY.val(e.scaleY);
        }
      };


  // Tooltip
  $('[data-toggle="tooltip"]').tooltip();


  // Cropper
  
  $image.on({
    'build.cropper': function (e) {
      console.log(e.type);
    },
    'built.cropper': function (e) {
      console.log(e.type);
    },
    'cropstart.cropper': function (e) {
      console.log(e.type, e.action);
    },
    'cropmove.cropper': function (e) {
      console.log(e.type, e.action);
    },
    'cropend.cropper': function (e) {
      console.log(e.type, e.action);
    },
    'crop.cropper': function (e) {
      console.log(e.x, e.y, e.width, e.height, e.rotate, e.scaleX, e.scaleY);
    },
  }).cropper(options);


  // Buttons
  if (!$.isFunction(document.createElement('canvas').getContext)) {
    $('button[data-method="getCroppedCanvas"]').prop('disabled', true);
  }

  if (typeof document.createElement('cropper').style.transition === 'undefined') {
    $('button[data-method="rotate"]').prop('disabled', true);
    $('button[data-method="scale"]').prop('disabled', true);
  }


  // Download
  // if (typeof $download[0].download === 'undefined') {
  //   $download.addClass('disabled');
  // }


  // Options
  $('.docs-toggles').on('change', 'input', function () {
    var $this = $(this);
    var name = $this.attr('name');
    var type = $this.prop('type');
    var cropBoxData;
    var canvasData;

    if (!$image.data('cropper')) {
      return;
    }

    if (type === 'checkbox') {
      options[name] = $this.prop('checked');
      cropBoxData = $image.cropper('getCropBoxData');
      canvasData = $image.cropper('getCanvasData');

      options.built = function () {
        $image.cropper('setCropBoxData', cropBoxData);
        $image.cropper('setCanvasData', canvasData);
      };
    } else if (type === 'radio') {
      options[name] = $this.val();
    }

    $image.cropper('destroy').cropper(options);
  });
  // Methods
  $('.docs-buttons').on('click', '[data-method]', function () {
    var $this = $(this);
    var data = $this.data();
    var $target;

    if ($this.prop('disabled') || $this.hasClass('disabled')) {
      return;
    }

    if ($image.data('cropper') && data.method) {
      data = $.extend({}, data); // Clone a new one

      if (typeof data.target !== 'undefined') {
        $target = $(data.target);

        if (typeof data.option === 'undefined') {
          try {
            data.option = JSON.parse($target.val());
          } catch (e) {
            console.log(e.message);
          }
        }
      }

      result = $image.cropper(data.method, data.option, data.secondOption);

      switch (data.method) {
        case 'scaleX':
        case 'scaleY':
          $(this).data('option', -data.option);
          break;

        case 'getCroppedCanvas':
          if (result) {

            // Bootstrap's Modal
            // console.log(result.toDataURL())
            setTimeout(function(){

            // $('.crop-image').removeClass('is_visible');
            // $http({
            //     method: 'POST',
            //     url: "/zapblog/image/",
            //     data:{
            //         'imageb64':result.toDataURL('image/jpeg')
            //     }
            // }).error(function(error){console.log(error)
            //     alert('Somthing went wrong while image uploading. Retry...')
            // }).then(function successCallback(response) {
            $('.crop-image').removeClass('is_visible');
            var html= "<div class='block' data-width='12'><div class='editable'><img class='blog_image' id="+ new Date().getTime() +" src="+result.toDataURL('image/jpeg')+"></div><div class='new-block'><ul><li class='text'>Text</li><li class='image'>Image</li><li class='embed'>Social Embed</li><li class='zap_embed'>Zapyle Product Embed</li><li class='button'>Button</li></ul></div><div class='edit-block'><ul><li class='move'>Move</li><li class='delete'>Delete</li></ul></div></div>"
            // $scope.new_place.after(html)
            // })
            //$scope.images_selected.push({'id':$scope.img_id,'img_url': result.toDataURL('image/jpeg')})
            // $scope.img_id=$scope.img_id+1;
            // $scope.$apply()
            // $scope.show_crop = false
            })
            // $('#getCroppedCanvasModal').modal().find('.modal-body').html(result);

            // if (!$download.hasClass('disabled')) {
            //   $download.attr('href', result.toDataURL('image/jpeg'));
            // }
          }

          break;
      }

      if ($.isPlainObject(result) && $target) {
        try {
          $target.val(JSON.stringify(result));
        } catch (e) {
          console.log(e.message);
        }
      }

    }
  });


  // Keyboard
  $(document.body).on('keydown', function (e) {

    if (!$image.data('cropper') || this.scrollTop > 300) {
      return;
    }

    switch (e.which) {
      case 37:
        e.preventDefault();
        $image.cropper('move', -1, 0);
        break;

      case 38:
        e.preventDefault();
        $image.cropper('move', 0, -1);
        break;

      case 39:
        e.preventDefault();
        $image.cropper('move', 1, 0);
        break;

      case 40:
        e.preventDefault();
        $image.cropper('move', 0, 1);
        break;
    }

  });

  var pic_objects = {}
  // Import image
  var $inputImage = $('#inputImage');
  var URL = window.URL || window.webkitURL;
  var blobURL;

  if (URL) {
    $inputImage.change(function () {
      // $scope.show_crop = true
      var files = this.files;
      var file;

      if (!$image.data('cropper')) {
        return;
      }

      if (files && files.length) {
        file = files[0];

        if (/^image\/\w+$/.test(file.type)) {
          blobURL = URL.createObjectURL(file);
          alert(blobURL)
          $image.one('built.cropper', function () {

            // Revoke when load complete
            URL.revokeObjectURL(blobURL);
          }).cropper('reset').cropper('replace', blobURL);
          // $inputImage.val('');
        } else {
          window.alert('Please choose an image file.');
        }
      }
    });
  } else {
    $inputImage.prop('disabled', true).parent().addClass('disabled');
  }

  $('body').on('click', '.pri-overlay.image .show-preview', function() {
    result = $image.cropper('getCroppedCanvas', null, null);
    // var html= "<img src="+result.toDataURL('image/jpeg')+">"
    // console.log(html)
    previewImage(result);
  });
  $('body').on('click', '.pri-overlay.image .back', function() {
    $('.pri-overlay.image').removeClass('preview-mode');
  });
});

  