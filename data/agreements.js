// Agreement facts extracted from SharePoint Commercial > 01. Accounts (AS SOLD).
// Keyed by Lift project code (Work Order). Refreshed on a weekly cadence, not by
// the nightly Lift pull, since agreements change rarely.
// v1: esVolta LTSA (source: Tollgate 3 Commercial Summary). More deals landing.
(function () {
  var esvolta = {
    folder: "esVolta LTSA - Acorn + Wildcat (AS SOLD)",
    url: "https://netorg282190.sharepoint.com/Shared%20Documents/Commercial/01.%20Accounts/esVolta/LTSAs%20-%20Wildcat%20%26%20Acorn/AS%20SOLD",
    hubspotDeal: "39040317453",
    contractValue: null,
    laborHoursBudget: null,
    expenseBudget: null,
    startDate: "2025-08-08",
    contractedEnd: "2026-08-07",
    term: "1-year term, auto-renews, 60-day cancellation notice, 3.5% annual escalation",
    source: "Tollgate 3 Commercial Summary (AS SOLD)"
  };
  function acorn() {
    return Object.assign({}, esvolta, {
      scope: "LTSA O&M for Acorn (Powin Stack225, Thousand Oaks CA). 2 techs, twice-annual PM (1 local + 1 regional) plus corrective and emergency reactive maintenance. Weekly operational calls; monthly reports by the 4th. Liquidated-damages exposure on response times; LD cap 10% of contract (about $2,198/yr for Acorn).",
      milestones: [{ date: "2026-08-07", label: "Contract term end (auto-renews unless 60-day notice)" }]
    });
  }
  function wildcat() {
    return Object.assign({}, esvolta, {
      scope: "LTSA O&M for Wildcat (Powin Stack225, Palm Springs CA). 2 techs, twice-annual PM (1 local + 1 regional) plus corrective and emergency reactive maintenance. Weekly operational calls; monthly reports by the 4th. Liquidated-damages exposure on response times; LD cap 10% of contract (about $2,522/yr for Wildcat).",
      milestones: [{ date: "2026-08-07", label: "Contract term end (auto-renews unless 60-day notice)" }]
    });
  }
  window.AGREEMENTS = {
    "ACORN CM_ESVOLTA_1068": acorn(),
    "ACORN PM_ESVOLTA_1069": acorn(),
    "WILDCAT CM_ESVOLTA_1066": wildcat(),
    "WILDCAT PM_ESVOLTA_1067": wildcat()
  };
})();
