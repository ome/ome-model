/*
 * #%L
 * OME XML library
 * %%
 * Copyright (C) 2014 - 2016 Open Microscopy Environment:
 *   - Board of Regents of the University of Wisconsin-Madison
 *   - Glencoe Software, Inc.
 *   - University of Dundee
 * %%
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 * #L%
 */

package ome.units.quantity;

import ome.units.unit.Unit;

/**
 * Temperature quantity.
 *
 * @since 5.1
 */
public class Temperature extends Quantity implements Comparable<Temperature>
{
  /** Seed for hashCode. */
  private static final int SEED1 = 12;
  /** Seed for hashCode. */
  private static final int SEED2 = 23;
  /** Value of this quantity. */
  Number value;
  /** Unit type of this quantity. */
  Unit<ome.units.quantity.Temperature> unit;
  /** Cached value for hashCode. */
  private int hashCodeValue;

  /**
   * Create an Temperature.
   *
   * @param inValue the value.
   * @param inUnit the unit type.
   */
  public Temperature(Number inValue,
    Unit<ome.units.quantity.Temperature> inUnit)
  {
    if (inValue == null)
    {
      throw new NullPointerException("Temperature: Temperature cannot be constructed with a null value.");
    }
    value = inValue;
    unit = inUnit;
    hashCodeValue = SEED1;
    hashCodeValue = SEED2 * hashCodeValue + Float.floatToIntBits(value.floatValue());
    hashCodeValue = SEED2 * hashCodeValue + unit.getSymbol().hashCode();
  }

  @Override
  public Number value()
  {
    return value;
  }

  /**
   * Perform a unit conversion.
   *
   * @param inUnit the unit to convert to.
   * @return the current quantity value converted to the specified
   * unit, or null if the conversion is not possible.
   */
  public Number value(Unit<ome.units.quantity.Temperature> inUnit)
  {
    if (unit.equals(inUnit))
    {
      return value;
    }
    if (unit.isConvertible(inUnit))
    {
      return unit.convertValue(value, inUnit);
    }
    return null;
  }

  /**
   * Check quantities for equality.
   *
   * Unit conversion will be performed when required to convert into
   * the unit system of this quantity in order to perform the
   * comparison.
   *
   * Note that floating point comparison is dangerous.  Do not use
   * this method.
   *
   * @return true if equal, false if not equal.
   */
  @Override
  public boolean equals(Object other)
  {
    if (other == null)
    {
      return false;
    }
    if (this.getClass() != other.getClass())
    {
      return false;
    }
    Temperature otherTemperature = (Temperature)other;
    if (unit.equals(otherTemperature.unit))
    {
      // Temperatures use same unit so compare value
      return value.equals(otherTemperature.value);
    } else {
      if (unit.isConvertible(otherTemperature.unit))
      {
        // Temperatures use different compatible units so convert value then compare
        return (unit.convertValue(value, otherTemperature.unit)).equals(otherTemperature.value);
      }
    }
    return false;
  }

  /**
   * Check quantities for equality.
   *
   * Unit conversion will be performed when required to convert into
   * the unit system of this quantity in order to perform the
   * comparison.
   *
   * Note that floating point comparison is dangerous.  Do not use
   * this method.
   *
   * @return true if equal, false if not equal.
   */
  @Override
  public int compareTo(Temperature other)
  {
    if (this == other) {
      return 0;
    }
    return Double.compare(value.doubleValue(), other.value(unit).doubleValue());
  }

  @Override
  public int hashCode()
  {
    return hashCodeValue;
  }
  @Override
  public String toString()
  {
      return this.getClass().getName() +
              ": " +
              "value[" +
              value +
              "], unit[" +
              unit.getSymbol() +
              "] stored as " +
              value.getClass().getName();
  }

  @Override
  public Unit<ome.units.quantity.Temperature> unit()
  {
    return unit;
  }
}
