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
import { ApiService } from '../services/api.service';
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
export class DashboardComponent implements OnInit{
  theme: string;
  selected: string = 'days';
  isLoading: boolean = true;
  mergeOptions: object = {};
  stats: any = {};
  pieOptions: object;
  barOptions: object;
  

  options = [
    { value: 'days', viewValue: 'Days (last 7 days)' },
    { value: 'weeks', viewValue: 'Weeks (last 4 weeks)' },
    { value: 'months', viewValue: 'Months (This year)' },
    { value: 'years', viewValue: 'Years (since start)' }
  ];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getStats()
      .subscribe((value: any) => {
        this.stats = value;
        this.pieOptions = {
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
              name: 'Area',
              type: 'pie',
              radius: [70, 110],
              data: [
                { value: this.stats.n_tagged_docs, name: 'Tagged Documents' },
                { value: this.stats.n_untagged_docs, name: 'Untagged Documents' }
              ],
              color: ['#39ff14', '#000000']
            }
          ]
        };
        this.barOptions = {
          title: {
            text: 'Document upload/Day',
            x: 'center'
          },
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
            color: ['#39ff14', '#000000'],
            data: this.stats.uploaded_last_7_days
          }]
        };
        this.isLoading = false;
      });
  }

  changeBar = (event) => {
    switch (event.value) {
      case 'days':
        this.mergeOptions = {
          title: {
            text: 'Document upload/Day',
            x: 'center'
          },
          xAxis: [
            {
              type: 'category',
              data: this.getPreviousDays(),
              axisTick: {
                alignWithLabel: true
              }
            }
          ],
          series: [{
            name: 'Documents Added',
            type: 'bar',
            barWidth: '50%',
            data: this.stats.uploaded_last_7_days
          }]
        };
        break;
      case 'weeks':
        var mondays = this.getPreviousMondays();
        this.mergeOptions = {
          title: {
            text: 'Document upload/Week',
            x: 'center'
          },
          xAxis: [
            {
              type: 'category',
              data: mondays,
              axisTick: {
                alignWithLabel: true
              }
            }
          ],
          series: [{
            name: 'Documents Added',
            type: 'bar',
            barWidth: '50%',
            data: this.stats.uploaded_last_4_weeks
          }]
        };
        break;
      case 'months':
        //var months = this.getPreviousMonths();
        var months = new Array("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec");

        this.mergeOptions = {
          title: {
            text: 'Document upload/Month',
            x: 'center'
          },
          xAxis: [
            {
              type: 'category',
              data: months,
              axisTick: {
                alignWithLabel: true
              }
            }
          ],
          series: [{
            name: 'Documents Added',
            type: 'bar',
            barWidth: '50%',
            data: this.stats.uploaded_this_year
          }]
        };
        break;
      case 'years':
        var years = this.getPreviousYears()
        this.mergeOptions = {
          title: {
            text: 'Document upload/Year',
            x: 'center'
          },
          xAxis: [
            {
              type: 'category',
              data: years,
              axisTick: {
                alignWithLabel: true
              }
            }
          ],
          series: [{
            name: 'Documents Added',
            type: 'bar',
            barWidth: '50%',
            data: this.stats.uploaded_all_years
          }]
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
