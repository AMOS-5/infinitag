/**
 * @license
 * InfiniTag
 * Copyright (c) 2020 AMOS-5.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import { Component, OnInit } from '@angular/core';

/**
 *
 * @class DashboardComponent
 *
 * Component representing the dashboard tab (no functionality right now)
 *
 */
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {
  theme: string;
  selected: string = 'days';
  mergeOptions: object = {};
  pieOptions = {
    title: {
      text: 'Tagged/Untagged Documents',
      x: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c} ({d}%)'
    },
    legend: {
      x: 'center',
      y: 'bottom',
      data: ['Tagged Documents', 'Untagged Documents']
    },
    calculable: true,
    series: [
      {
        name: 'area',
        type: 'pie',
        radius: [70, 110],
        data: [
          { value: 10, name: 'Tagged Documents' },
          { value: 90, name: 'Untagged Documents' }
        ]
      }
    ]
  };

  barOptions = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        axisTick: {
          alignWithLabel: true
        }
      }
    ],
    yAxis: [{
      type: 'value'
    }],
    series: [{
      name: 'Documents Added',
      type: 'bar',
      barWidth: '50%',
      data: [3, 5, 10, 3, 5, 2, 4, 4, 5, 12, 11, 12]
    }]
  };

  options = [
    { value: 'days', viewValue: 'Days (last 7 days)' },
    { value: 'weeks', viewValue: 'Weeks (last 4 weeks)' },
    { value: 'months', viewValue: 'Months (last 12 months)' },
    { value: 'years', viewValue: 'Years (since start)' }
  ];

  changeBar = (event) => {
    switch (event.value) {
      case 'days':
        this.mergeOptions = {
          xAxis: [
            {
              type: 'category',
              data: this.getPreviousDays(),
              axisTick: {
                alignWithLabel: true
              }
            }
          ],
        };
        break;
      case 'weeks':
        var mondays = this.getPreviousMondays();
        this.mergeOptions = {
          xAxis: [
            {
              type: 'category',
              data: mondays,
              axisTick: {
                alignWithLabel: true
              }
            }
          ],
        };
        break;
      case 'months':
        var months = this.getPreviousMonths();
        console.log(months)
        this.mergeOptions = {
          xAxis: [
            {
              type: 'category',
              data: months,
              axisTick: {
                alignWithLabel: true
              }
            }
          ],
        };
        break;
      case 'years':
        var years = this.getPreviousYears()
        this.mergeOptions = {
          xAxis: [
            {
              type: 'category',
              data: years,
              axisTick: {
                alignWithLabel: true
              }
            }
          ],
        };
        break;
      default:
        this.mergeOptions = {
          xAxis: [
            {
              type: 'category',
              data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
              axisTick: {
                alignWithLabel: true
              }
            }
          ],
        };
    }

  }

  getPreviousDays = () => {
    var days = [];
    var daysName = new Array("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat");
    for (var i = 0; i < 7; i++) {
      var d = new Date();
      d.setDate(d.getDate() - i);
      days.push(daysName[d.getDay()])
    }
    return days.reverse();
  }

  getPreviousMondays = () => {
    var prevMondays = [];
    var d = new Date();

    let dt = new Date(d.setDate(d.getDate() - (d.getDay() + 6) % 7));
    prevMondays.push(dt.getDate() + "/" + (dt.getMonth() + 1));

    for (let i = 0; i < 3; i++) {
      let dt = new Date(d.setDate(d.getDate() - ((d.getDay() + 6) % 7) - 7));
      prevMondays.push(dt.getDate() + "/" + (dt.getMonth() + 1));
    }
    return prevMondays.reverse();
  }

  getPreviousMonths = () => {
    var monthsWeWant = [];
    var monthName = new Array("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec");

    var d = new Date();
    d.setDate(1);

    for (let i = 0; i <= 11; i++) {
      monthsWeWant.push(monthName[d.getMonth()]);
      d.setMonth(d.getMonth() - 1);
    }
    return monthsWeWant.reverse();
  }

  getPreviousYears = () => {
    var years = [];
    var d = new Date();
    let index = 0;
    console.log(d.getFullYear())
    for (let i = 2020; i <= d.getFullYear(); i++) {
      years.push(2020 + index);
      index++;
    }
    return years;
  }
}
