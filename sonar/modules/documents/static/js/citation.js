// SPDX-FileCopyrightText: Fondation RERO+
// SPDX-License-Identifier: AGPL-3.0-or-later

$(document).ready(function () {
  const $citationModal = $('#citationModal');
  if ($citationModal.length === 0) {
    return;
  }

  const stylesUrl = $citationModal.data('styles-url');
  const citationUrl = $citationModal.data('citation-url');
  const i18n = {
    loading: $citationModal.data('i18n-loading'),
    selectStyle: $citationModal.data('i18n-select-style'),
    errorStyles: $citationModal.data('i18n-error-styles'),
    errorCitation: $citationModal.data('i18n-error-citation'),
  };

  const $citationStyles = $('#citation-styles');
  const $citationText = $('#citation-text');
  const $citationCopy = $('#citation-copy');
  const $citationMessage = $('#citation-message');
  const $citationToast = $('#citation-toast');
  let citationStylesLoaded = false;
  let citationStylesLoading = false;
  let citationRequestId = 0;

  const showCopiedToast = function () {
    $citationToast.toast('show');
  };

  const showCitationMessage = function (message) {
    $citationMessage.text(message).removeClass('d-none alert-danger').addClass('alert-danger');
  };

  const clearCitationMessage = function () {
    $citationMessage.addClass('d-none').text('');
  };

  const loadCitation = function (styleId) {
    citationRequestId += 1;
    const requestId = citationRequestId;

    $citationStyles.find('button').removeClass('font-weight-bold');
    $citationStyles.find('button[data-style="' + styleId + '"]').addClass('font-weight-bold');
    $citationText.text(i18n.loading);
    $citationCopy.addClass('d-none');

    fetch(citationUrl + '?style=' + encodeURIComponent(styleId))
      .then(function (response) {
        if (!response.ok) {
          throw new Error('citation request failed');
        }
        return response.json();
      })
      .then(function (data) {
        if (requestId !== citationRequestId) {
          return;
        }
        $citationText.html(data.citation);
        $citationCopy.removeClass('d-none');
        clearCitationMessage();
      })
      .catch(function () {
        if (requestId !== citationRequestId) {
          return;
        }
        $citationText.text(i18n.selectStyle);
        showCitationMessage(i18n.errorCitation);
      });
  };

  $citationCopy.click(function () {
    const html = $citationText.html();
    const text = $citationText.text();

    if (!navigator.clipboard) {
      return;
    }

    if (window.ClipboardItem) {
      const item = new ClipboardItem({
        'text/plain': new Blob([text], { type: 'text/plain' }),
        'text/html': new Blob([html], { type: 'text/html' }),
      });
      navigator.clipboard
        .write([item])
        .then(showCopiedToast)
        .catch(function () {
          navigator.clipboard.writeText(text).then(showCopiedToast);
        });
    } else {
      navigator.clipboard.writeText(text).then(showCopiedToast);
    }
  });

  $citationModal.on('show.bs.modal', function () {
    if (citationStylesLoaded || citationStylesLoading) {
      return;
    }
    citationStylesLoading = true;

    fetch(stylesUrl)
      .then(function (response) {
        if (!response.ok) {
          throw new Error('citation styles request failed');
        }
        return response.json();
      })
      .then(function (styles) {
        citationStylesLoaded = true;
        styles.forEach(function (style) {
          const $li = $('<li>');
          const $button = $(
            '<button type="button" class="btn btn-link p-0 d-block text-left" data-style="' + style.id + '">' + style.label + '</button>'
          );
          $button.click(function () {
            loadCitation(style.id);
          });
          $li.append($button);
          $citationStyles.append($li);
        });
      })
      .catch(function () {
        showCitationMessage(i18n.errorStyles);
      })
      .finally(function () {
        citationStylesLoading = false;
      });
  });
});
