"use strict";

Date.prototype.toYearString = function () {
    return this.getFullYear().toString();
};
Date.prototype.toMonthString = function () {
    return (this.getMonth() + 1).toString().padStart(2, '0');
};
Date.prototype.toDateString = function () {
    return this.getDate().toString().padStart(2, '0');
};
Date.prototype.toHourString = function () {
    return this.getHours().toString().padStart(2, '0');
};
Date.prototype.toMinuteString = function () {
    return this.getMinutes().toString().padStart(2, '0');
};
Date.prototype.toSecondString = function () {
    return this.getSeconds().toString().padStart(2, '0');
};
Date.prototype.toLocaleDateString = function () {
    return [
        this.toYearString(),
        this.toMonthString(),
        this.toDateString(),
    ].join('-');
};
Date.prototype.toLocaleTimeString = function () {
    return [
        this.toHourString(),
        this.toMinuteString(),
        this.toSecondString(),
    ].join(':');
};
Date.prototype.toLocaleString = function () {
    return [
        this.toLocaleDateString(),
        this.toLocaleTimeString(),
    ].join(' ');
};
