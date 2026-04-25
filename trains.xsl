<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output method="html" encoding="UTF-8" indent="yes"/>

    <!-- key to get station name by id -->
    <xsl:key name="st" match="station" use="@id"/>

    <xsl:template match="/">
        <html lang="en">
        <head>
            <meta charset="UTF-8"/>
            <title>Train Trips Report</title>
            <style>
                /* general */
                body {
                    font-family: Arial, sans-serif;
                    background-color: #ffffff;
                    color: #000000;
                    margin: 0;
                    padding: 0;
                }
                /* navigation */
                .topbar {
                    background-color: #003399;
                    padding: 10px 20px;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                }
                /* page content */
                .wrap {
                    max-width: 1000px;
                    margin: 25px auto;
                    padding: 0 20px 40px;
                }
                /* page title */
                .ptitle {
                    font-size: 20px;
                    color: #000000;
                    border-bottom: 2px solid #0066cc;
                    padding-bottom: 6px;
                    margin-bottom: 20px;
                }
                /* author note box */
                .note {
                    background: #ffffff;
                    border: 1px solid #999999;
                    padding: 10px 14px;
                    margin-bottom: 20px;
                    font-size: 13px;
                    color: #555;
                } 
                /* line card */
                .lcard {
                    background: #ffffff;
                    border: 1px solid #999999;
                    margin-bottom: 20px;
                }
                /* line header bar */
                .lhead {
                    background-color: #003399;
                    color: #ffffff;
                    padding: 10px 16px;
                    font-size: 15px;
                    font-weight: bold;
                }
                /* trips section label */
                .tlbl {
                    color: #cc0000;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 10px 16px 4px;
                }
                /* single trip block */
                .trip {
                    padding: 10px 16px 16px;
                    border-top: 1px solid #eeeeee;
                }
                /* trip code */
                .tcode {
                    color: #0066cc;
                    font-size: 14px;
                    font-weight: bold;
                    text-decoration: underline;
                    margin-bottom: 4px;
                }
                /* trip route text */
                .troute {
                    color: #555555;
                    font-size: 13px;
                    margin-bottom: 8px;
                }
                /* schedule / class / price table */
                table.ttable {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 13px;
                    margin-top: 6px;
                }
                table.ttable thead tr {
                    background-color: #003399;
                    color: #ffffff;
                    text-align: left;
                }
                table.ttable thead th {
                    padding: 7px 12px;
                    border: 1px solid #003399;
                }
                table.ttable tbody td {
                    padding: 6px 12px;
                    border: 1px solid #cccccc;
                }
                table.ttable tbody tr:nth-child(even) {
                    background-color: #e8e8e8;
                }
                /* vip row in red */
                .vrow td { color: #cc0000; font-weight: bold; }
                .vip     { color: #cc0000; font-weight: bold; }
                /* footer */
                .foot {
                    background-color: #003399;
                    color: #ffffff;
                    text-align: center;
                    padding: 12px;
                    font-size: 13px;
                    margin-top: 30px;
                }
            </style>
        </head>
        <body>

            <div class="topbar">
                <img src="static/images/logo.svg" alt="Logo" style="height: 24px; vertical-align: middle; margin-right: 10px; border-radius: 4px;"/>
                Railway Trip Management
            </div>

            <div class="wrap">

                <h1 class="ptitle">Train Trips Report</h1>

                <!-- student name and group -->
                <div class="note">
                    <strong>This page is implemented by the student:</strong> ... /
                    <strong>Group:</strong> ...
                </div>

                <!-- loop through each line -->
                <xsl:for-each select="transport/lines/line">
                    <xsl:variable name="did"   select="@departure"/>
                    <xsl:variable name="aid"   select="@arrival"/>
                    <xsl:variable name="dname" select="key('st', $did)/@name"/>
                    <xsl:variable name="aname" select="key('st', $aid)/@name"/>

                    <div class="lcard">

                        <div class="lhead">
                            Line <xsl:value-of select="@code"/> :
                            <xsl:value-of select="$dname"/> to <xsl:value-of select="$aname"/>
                        </div>

                        <div class="tlbl">Detailed List of Trips:</div>

                        <!-- loop through each trip -->
                        <xsl:for-each select="trips/trip">
                            <xsl:variable name="tcode" select="@code"/>
                            <xsl:variable name="ttype" select="@type"/>

                            <div class="trip">

                                <div class="tcode">Trip: <xsl:value-of select="$tcode"/></div>

                                <div class="troute">
                                    <xsl:value-of select="$dname"/> -&gt; <xsl:value-of select="$aname"/>
                                </div>

                                <table class="ttable">
                                    <thead>
                                        <tr>
                                            <th>Schedule</th>
                                            <th>Train Type</th>
                                            <th>Class</th>
                                            <th>Price (DA)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <xsl:for-each select="class">
                                            <xsl:variable name="ctype"  select="@type"/>
                                            <xsl:variable name="cprice" select="@price"/>

                                            <!-- VIP in red, Economy normal -->
                                            <xsl:choose>
                                                <xsl:when test="$ctype = 'VIP'">
                                                    <tr class="vrow">
                                                        <td><xsl:value-of select="../schedule/@departure"/> - <xsl:value-of select="../schedule/@arrival"/></td>
                                                        <td><xsl:value-of select="$ttype"/></td>
                                                        <td class="vip">VIP</td>
                                                        <td class="vip"><xsl:value-of select="$cprice"/></td>
                                                    </tr>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <tr>
                                                        <td><xsl:value-of select="../schedule/@departure"/> - <xsl:value-of select="../schedule/@arrival"/></td>
                                                        <td><xsl:value-of select="$ttype"/></td>
                                                        <td>Economy</td>
                                                        <td><xsl:value-of select="$cprice"/></td>
                                                    </tr>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </xsl:for-each>
                                    </tbody>
                                </table>

                            </div>
                        </xsl:for-each>

                    </div>
                </xsl:for-each>

            </div>

            <div class="foot">UMBB - FS | CS Department 2025/2026 | L3 DSS Project</div>

        </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
